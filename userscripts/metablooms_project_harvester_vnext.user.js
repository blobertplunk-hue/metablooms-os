// ==UserScript==
// @name         MetaBlooms Project Harvester vNext (Hardened, Fail-Closed, Resumable, Sharded)
// @namespace    metablooms.harvester
// @version      5.0.0
// @description  Deterministic, fail-closed Project harvester for ChatGPT Projects: robust link enumeration, forced full history load, message-level extraction, sharded exports, resumable runs, telemetry UI.
// @match        https://chatgpt.com/*
// @match        https://chat.openai.com/*
// @run-at       document-idle
// @grant        GM_download
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_deleteValue
// @grant        GM_registerMenuCommand
// ==/UserScript==

(function () {
  "use strict";

  /********************************************************************
   * CONFIG
   ********************************************************************/
  const CFG = {
    hotkey: { alt: true, key: "e" },

    // Determinism / bounds
    tickMs: 350,
    settleMs: 900,
    quietMs: 900,
    maxReadyMs: 12000,
    maxRuntimeMs: 60 * 60 * 1000,
    maxRetriesPerChat: 3,

    // Project list enumeration
    maxChats: 50000,
    listScrollPasses: 650,
    listScrollPauseMs: 240,
    stablePassesToStop: 10,
    lowCountFailClosed: 12,
    allowLowCountOverride: false,

    // Transcript full-history forcing
    transcriptScrollPasses: 48,
    transcriptScrollPauseMs: 260,
    transcriptStablePasses: 6,
    transcriptMinMessagesWarn: 2,

    // Export
    exportPrefix: "metablooms_export",
    shardMaxBytes: 10 * 1024 * 1024, // 10MB shards
    saveAs: true,

    // UI
    panelSide: "left",
    panelTopPx: 120,
    panelWidthPx: 430,
    telemetryMax: 1200,
  };

  /********************************************************************
   * ERROR TAXONOMY (Script-ECL style)
   ********************************************************************/
  class FailClosedError extends Error { constructor(msg, meta) { super(msg); this.name = "FailClosedError"; this.meta = meta || {}; } }
  class AuthError       extends Error { constructor(msg, meta) { super(msg); this.name = "AuthError"; this.meta = meta || {}; } }
  class SelectorError   extends Error { constructor(msg, meta) { super(msg); this.name = "SelectorError"; this.meta = meta || {}; } }
  class StabilityError  extends Error { constructor(msg, meta) { super(msg); this.name = "StabilityError"; this.meta = meta || {}; } }
  class DownloadError   extends Error { constructor(msg, meta) { super(msg); this.name = "DownloadError"; this.meta = meta || {}; } }
  class NavigationError extends Error { constructor(msg, meta) { super(msg); this.name = "NavigationError"; this.meta = meta || {}; } }

  function classifyError(e) {
    const n = e?.name || "UnknownError";
    const terminal = (n === "AuthError" || n === "FailClosedError");
    return { type: n, terminal };
  }

  /********************************************************************
   * STATE (resumable)
   ********************************************************************/
  const STATE_KEY = "MBX_VNEXT_RUNSTATE_v5_0_0";

  const DEFAULT_STATE = {
    version: "5.0.0",
    createdAt: null,
    startedAt: null,
    lastProgressAt: null,
    runId: null,
    running: false,
    pausedReason: null,

    // Pipeline cursor
    phase: "IDLE", // IDLE | ENUM_LINKS | PROCESS_CHAT | STOPPED | PAUSED
    links: [],
    index: 0,

    // per-chat bookkeeping
    chats: {}, // { url: { status, retries, convoId, messageCount, fingerprint, shards:[], error } }

    // outputs cached for downloads
    runManifest: null,

    // telemetry
    telemetry: [],
  };

  function loadState() {
    const s = GM_getValue(STATE_KEY, null);
    if (!s || typeof s !== "object") return structuredClone(DEFAULT_STATE);
    // fail-closed if schema mismatch is extreme; otherwise tolerate new keys
    return Object.assign(structuredClone(DEFAULT_STATE), s);
  }
  function saveState() { GM_setValue(STATE_KEY, STATE); }
  function resetState() { GM_deleteValue(STATE_KEY); location.reload(); }

  let STATE = loadState();

  /********************************************************************
   * UTIL
   ********************************************************************/
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const nowIso = () => new Date().toISOString();
  const txt = (el) => (el?.innerText || el?.textContent || "").trim();

  function emit(event_type, data = {}) {
    STATE.telemetry.push({ ts: nowIso(), event_type, phase: STATE.phase, ...data });
    if (STATE.telemetry.length > CFG.telemetryMax) STATE.telemetry = STATE.telemetry.slice(-CFG.telemetryMax);
    saveState();
    refreshUI();
  }

  function assertSessionOk() {
    // conservative auth detection
    if (location.pathname.includes("/auth/")) throw new AuthError("Auth route detected", { url: location.href });
    const t = (document.documentElement && document.documentElement.innerText) ? document.documentElement.innerText : "";
    if (t.includes("Sign in") && t.includes("Log in")) throw new AuthError("Sign-in page detected", { url: location.href });
  }

  function normalizeUrl(u) {
    try { const url = new URL(u, location.origin); url.hash = ""; return url.toString(); }
    catch { return u; }
  }

  function convoIdFromUrl(u) {
    try { const url = new URL(u, location.origin); const m = url.pathname.match(/\/c\/([^\/]+)/); return m ? m[1] : ""; }
    catch { return ""; }
  }

  async function waitStable(ms = CFG.settleMs) {
    let last = Date.now();
    const obs = new MutationObserver(() => (last = Date.now()));
    obs.observe(document.body, { subtree: true, childList: true, characterData: true });
    while (Date.now() - last < ms) await sleep(160);
    obs.disconnect();
  }

  async function waitForQuiet(el, quietMs = CFG.quietMs, maxMs = CFG.maxReadyMs) {
    let lastMut = Date.now();
    const mo = new MutationObserver(() => { lastMut = Date.now(); });
    mo.observe(el, { childList: true, subtree: true, characterData: true });
    const start = Date.now();
    while (Date.now() - start < maxMs) {
      if (Date.now() - lastMut >= quietMs) { mo.disconnect(); return true; }
      await sleep(120);
    }
    mo.disconnect();
    return false;
  }

  // tiny hash (non-crypto) for stabilization fingerprints
  function fnv1a(str) {
    let h = 0x811c9dc5;
    for (let i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = (h + ((h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24))) >>> 0;
    }
    return ("0000000" + h.toString(16)).slice(-8);
  }

  /********************************************************************
   * UI (panel + pill)
   ********************************************************************/
  function el(id) { return document.getElementById(id); }

  function ensureUI() {
    if (el("mbxv5-panel")) return;

    const panel = document.createElement("div");
    panel.id = "mbxv5-panel";
    panel.style.position = "fixed";
    panel.style.top = `${CFG.panelTopPx}px`;
    panel.style[CFG.panelSide] = "12px";
    panel.style.zIndex = "999999";
    panel.style.width = `${CFG.panelWidthPx}px`;
    panel.style.display = "none";

    panel.innerHTML = `
      <div style="
        background:#0b0f14; color:#e6edf3;
        border:1px solid rgba(230,237,243,.18);
        border-radius:14px;
        box-shadow: 0 18px 48px rgba(0,0,0,.55);
        padding:12px;
        font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
        font-size:12.5px;
      ">
        <div style="display:flex; align-items:center; justify-content:space-between; gap:10px;">
          <div style="font-weight:850;">MetaBlooms Harvester vNext</div>
          <div style="display:flex; gap:8px; align-items:center;">
            <span style="opacity:.75;">Alt+E</span>
            <button id="mbxv5-hide" style="cursor:pointer; background:#111827; color:#e6edf3; border:1px solid rgba(230,237,243,.18); border-radius:10px; padding:5px 9px;">Hide</button>
          </div>
        </div>

        <div id="mbxv5-status" style="margin:10px 0 8px; color:#cbd5e1;">Idle.</div>

        <div style="height:10px; background:rgba(230,237,243,.10); border-radius:10px; overflow:hidden;">
          <div id="mbxv5-bar" style="height:10px; width:0%; background:rgba(56,189,248,.92);"></div>
        </div>

        <div style="display:flex; gap:8px; margin:12px 0 10px; flex-wrap:wrap;">
          <button id="mbxv5-start" style="cursor:pointer; background:#1f2937; color:#e6edf3; border:1px solid rgba(230,237,243,.18); border-radius:12px; padding:7px 11px;">Start</button>
          <button id="mbxv5-stop" style="cursor:pointer; background:#3b0a0a; color:#fecaca; border:1px solid rgba(252,165,165,.32); border-radius:12px; padding:7px 11px;">Stop</button>
          <button id="mbxv5-manifest" style="cursor:pointer; background:#0f172a; color:#e6edf3; border:1px solid rgba(230,237,243,.18); border-radius:12px; padding:7px 11px;" disabled>Download Manifest</button>
          <button id="mbxv5-tele" style="cursor:pointer; background:#0f172a; color:#e6edf3; border:1px solid rgba(230,237,243,.18); border-radius:12px; padding:7px 11px;">Telemetry</button>
          <button id="mbxv5-reset" style="cursor:pointer; background:#111827; color:#e6edf3; border:1px solid rgba(230,237,243,.18); border-radius:12px; padding:7px 11px;">Reset</button>
        </div>

        <div style="margin:6px 0 10px; font-size:11.5px; color:#9ca3af;">
          <div><b style="color:#e6edf3;">Phase:</b> <span id="mbxv5-phase">—</span></div>
          <div><b style="color:#e6edf3;">Progress:</b> <span id="mbxv5-prog">0 / 0</span></div>
          <div><b style="color:#e6edf3;">Last URL:</b> <span id="mbxv5-last">—</span></div>
          <div><b style="color:#e6edf3;">Paused:</b> <span id="mbxv5-paused">—</span></div>
        </div>

        <div>
          <div style="font-weight:750; margin-bottom:6px;">Log</div>
          <textarea id="mbxv5-log" readonly style="
            width:100%; height:150px; resize:vertical;
            background:#05070a; color:#e6edf3;
            border:1px solid rgba(230,237,243,.16); border-radius:12px; padding:9px;
          "></textarea>
        </div>
      </div>
    `;
    document.body.appendChild(panel);

    const pill = document.createElement("div");
    pill.id = "mbxv5-pill";
    pill.style.position = "fixed";
    pill.style.left = "12px";
    pill.style.bottom = "12px";
    pill.style.zIndex = "999998";
    pill.style.display = "none";
    pill.style.padding = "8px 10px";
    pill.style.borderRadius = "999px";
    pill.style.background = "rgba(11,15,20,.92)";
    pill.style.color = "#e6edf3";
    pill.style.border = "1px solid rgba(230,237,243,.18)";
    pill.style.boxShadow = "0 10px 28px rgba(0,0,0,.45)";
    pill.style.fontFamily = "system-ui, -apple-system, Segoe UI, Roboto, sans-serif";
    pill.style.fontSize = "12px";
    pill.style.cursor = "pointer";
    pill.title = "Click to open harvester panel (Alt+E)";
    pill.textContent = "Harvester: idle";
    pill.addEventListener("click", () => setPanelVisible(true));
    document.body.appendChild(pill);

    el("mbxv5-hide").addEventListener("click", () => setPanelVisible(false));
    el("mbxv5-start").addEventListener("click", startRun);
    el("mbxv5-stop").addEventListener("click", requestStop);
    el("mbxv5-reset").addEventListener("click", resetState);
    el("mbxv5-tele").addEventListener("click", downloadTelemetry);
    el("mbxv5-manifest").addEventListener("click", downloadManifest);

    refreshUI();
  }

  function setPanelVisible(v) {
    ensureUI();
    el("mbxv5-panel").style.display = v ? "block" : "none";
    el("mbxv5-pill").style.display = (!v && STATE.running) ? "block" : "none";
  }

  function uiStatus(s) { ensureUI(); el("mbxv5-status").textContent = s; }

  function logLine(s) {
    ensureUI();
    const ta = el("mbxv5-log");
    const line = `[${new Date().toLocaleTimeString()}] ${s}`;
    ta.value = (ta.value ? ta.value + "\n" : "") + line;
    ta.scrollTop = ta.scrollHeight;
  }

  function setProgress(done, total) {
    ensureUI();
    el("mbxv5-prog").textContent = `${done} / ${total}`;
    const pct = total ? Math.round((done / total) * 100) : 0;
    el("mbxv5-bar").style.width = `${pct}%`;
  }

  function refreshUI() {
    if (!document.body) return;
    ensureUI();
    el("mbxv5-phase").textContent = STATE.phase || "—";
    el("mbxv5-paused").textContent = STATE.pausedReason || "—";
    el("mbxv5-last").textContent = STATE.links?.[STATE.index] || "—";
    setProgress(STATE.index || 0, STATE.links?.length || 0);
    el("mbxv5-manifest").disabled = !(STATE.runManifest && STATE.running === false);
    el("mbxv5-pill").style.display = (STATE.running && el("mbxv5-panel").style.display === "none") ? "block" : "none";
    el("mbxv5-pill").textContent = STATE.running ? `Harvesting ${Math.min((STATE.index||0)+1, STATE.links.length||0)}/${STATE.links.length||0}…` : "Harvester: idle";
  }

  document.addEventListener("keydown", (e) => {
    if (!!CFG.hotkey.alt === e.altKey && e.key.toLowerCase() === CFG.hotkey.key) {
      ensureUI();
      const visible = el("mbxv5-panel").style.display === "block";
      setPanelVisible(!visible);
    }
  });

  function registerMenu() {
    if (typeof GM_registerMenuCommand !== "function") return;
    GM_registerMenuCommand("MetaBlooms vNext: Start", startRun);
    GM_registerMenuCommand("MetaBlooms vNext: Stop", requestStop);
    GM_registerMenuCommand("MetaBlooms vNext: Telemetry JSON", downloadTelemetry);
    GM_registerMenuCommand("MetaBlooms vNext: Download Manifest", downloadManifest);
    GM_registerMenuCommand("MetaBlooms vNext: RESET (wipe state)", resetState);
  }

  /********************************************************************
   * DISCOVERY: robust project list container + enumeration
   ********************************************************************/
  function findLikelyProjectListContainer() {
    // Heuristic: pick container with lots of /c/ links, penalize transcriptish content
    const thread = document.querySelector("#thread");
    const rootCandidates = thread ? [...thread.querySelectorAll("div,aside,section,nav")] : [...document.querySelectorAll("aside,nav,section,div")];
    let best = null, bestScore = 0;

    for (const c of rootCandidates) {
      const count = c.querySelectorAll('a[href*="/c/"]').length;
      if (count < 3) continue;
      const transcriptish = c.querySelector('[data-message-author-role]') ? 1 : 0;
      const score = count - (transcriptish ? 10 : 0);
      if (score > bestScore) { bestScore = score; best = c; }
    }
    return best;
  }

  function forceScrollable(el) {
    try {
      el.style.overflowY = "auto";
      el.style.maxHeight = "75vh";
      el.style.scrollBehavior = "auto";
      return true;
    } catch { return false; }
  }

  function enumerateVisibleLinks(container) {
    const links = [...container.querySelectorAll('a[href*="/c/"]')];
    const out = [];
    for (const a of links) {
      const href = a.href;
      if (!href) continue;
      const u = normalizeUrl(href);
      if (!u.includes("/c/")) continue;
      out.push(u);
    }
    return out;
  }

  async function enumerateAllLinksFailClosed() {
    const container = findLikelyProjectListContainer();
    if (!container) throw new SelectorError("Project list container not found", { where: "findLikelyProjectListContainer" });

    forceScrollable(container);

    const seen = new Set();
    let stable = 0;
    let lastCount = 0;

    for (let pass = 0; pass < CFG.listScrollPasses; pass++) {
      const batch = enumerateVisibleLinks(container);
      for (const u of batch) {
        if (seen.size >= CFG.maxChats) break;
        seen.add(u);
      }

      if (seen.size === lastCount) stable++;
      else stable = 0;

      lastCount = seen.size;
      uiStatus(`Enumerating links… pass ${pass + 1}/${CFG.listScrollPasses} | found ${seen.size} | stable ${stable}/${CFG.stablePassesToStop}`);
      if (stable >= CFG.stablePassesToStop) break;

      // scroll down
      container.scrollTop = container.scrollHeight;
      await sleep(CFG.listScrollPauseMs);
    }

    const links = [...seen];
    if (links.length <= CFG.lowCountFailClosed && !CFG.allowLowCountOverride) {
      throw new FailClosedError("Suspiciously low conversation count (fail-closed)", {
        found: links.length,
        lowCountFailClosed: CFG.lowCountFailClosed,
      });
    }
    return links;
  }

  /********************************************************************
   * NAVIGATION
   ********************************************************************/
  async function gotoUrl(url) {
    const target = normalizeUrl(url);
    if (normalizeUrl(location.href) !== target) {
      location.href = target;
      await waitStable(CFG.settleMs);
    }
    // Give time for transcript container to mount
    await sleep(120);
  }

  /********************************************************************
   * TRANSCRIPT LOCATOR + FULL HISTORY LOAD (stabilization gate)
   ********************************************************************/
  function findTranscriptRoot() {
    // Prefer role-tagged message containers when available
    const roleNode = document.querySelector('[data-message-author-role]');
    if (roleNode) {
      // walk up to a scrollable-ish ancestor
      let cur = roleNode;
      for (let i = 0; i < 8 && cur; i++) {
        const st = getComputedStyle(cur);
        if (st && (st.overflowY === "auto" || st.overflowY === "scroll")) return cur;
        cur = cur.parentElement;
      }
    }
    // fallback: main
    const main = document.querySelector("main");
    if (main) return main;
    throw new SelectorError("Transcript root not found", { selectors: ["[data-message-author-role]", "main"] });
  }

  function messageNodes() {
    // Most stable signal you used across scripts:
    const nodes = [...document.querySelectorAll('[data-message-author-role]')];
    // fallback: attempt to infer from articles if role tags absent
    if (nodes.length) return nodes;
    const articles = [...document.querySelectorAll("main article, main [role='article'], article")];
    return articles;
  }

  function transcriptFingerprint() {
    const nodes = messageNodes();
    const first = txt(nodes[0] || "").slice(0, 120);
    const last  = txt(nodes[nodes.length - 1] || "").slice(0, 120);
    const base = `${nodes.length}|${first}|${last}`;
    return { count: nodes.length, fp: fnv1a(base) };
  }

  function clickLoadMoreIfPresent() {
    const candidates = [...document.querySelectorAll("button, a")];
    for (const b of candidates) {
      const t = txt(b).toLowerCase();
      if (!t) continue;
      if (t.includes("load more") || t.includes("show more") || t.includes("show earlier") || t.includes("load earlier")) {
        try { b.click(); return true; } catch { /* ignore */ }
      }
    }
    return false;
  }

  async function forceFullHistoryLoadFailClosed() {
    const root = findTranscriptRoot();

    // stabilization requires: message count + fingerprint plateau
    let stable = 0;
    let last = transcriptFingerprint();

    for (let pass = 0; pass < CFG.transcriptScrollPasses; pass++) {
      // attempt: scroll up strongly (older messages load)
      try { root.scrollTop = 0; } catch { /* ignore */ }
      clickLoadMoreIfPresent();

      await sleep(CFG.transcriptScrollPauseMs);
      await waitStable(260);

      const cur = transcriptFingerprint();
      const same = (cur.count === last.count && cur.fp === last.fp);
      stable = same ? (stable + 1) : 0;
      last = cur;

      uiStatus(`Loading full history… pass ${pass + 1}/${CFG.transcriptScrollPasses} | msgs=${cur.count} | stable ${stable}/${CFG.transcriptStablePasses}`);
      if (stable >= CFG.transcriptStablePasses) break;
    }

    // Quiet window and re-check fingerprint to ensure no late loads
    const quietOk = await waitForQuiet(root, CFG.quietMs, CFG.maxReadyMs);
    if (!quietOk) throw new StabilityError("Transcript did not enter quiet window (fail-closed)", { quietMs: CFG.quietMs });

    const after = transcriptFingerprint();
    const sameAfter = (after.count === last.count && after.fp === last.fp);
    if (!sameAfter) {
      throw new StabilityError("Transcript changed after stabilization (fail-closed)", { before: last, after });
    }

    if (after.count < CFG.transcriptMinMessagesWarn) {
      emit("WARN_LOW_TURNS", { messageCount: after.count });
    }
    return after;
  }

  /********************************************************************
   * EXTRACTION (message-level)
   ********************************************************************/
  function extractMessages() {
    const nodes = messageNodes();
    const out = [];

    for (let i = 0; i < nodes.length; i++) {
      const n = nodes[i];
      const role = n.getAttribute?.("data-message-author-role") || "unknown";
      const textContent = txt(n);

      // capture code blocks (best-effort)
      const codeBlocks = [];
      const pres = n.querySelectorAll ? n.querySelectorAll("pre") : [];
      for (const pre of pres) {
        const code = txt(pre);
        if (code) codeBlocks.push(code);
      }

      const digest = fnv1a(`${role}|${textContent.slice(0, 400)}|${codeBlocks.length}|${i}`);
      out.push({ i, role, text: textContent, codeBlocks, digest });
    }
    return out;
  }

  function buildChatArtifact(url, stabilized) {
    const convoId = convoIdFromUrl(url) || "unknown";
    const messages = extractMessages();
    const fp = fnv1a(messages.map(m => m.digest).join("|"));

    return {
      schema: "metablooms.chat.export.vnext",
      exportedAt: nowIso(),
      url: normalizeUrl(url),
      convoId,
      stabilized: { messageCount: stabilized.count, fingerprint: stabilized.fp },
      extracted: { messageCount: messages.length, digest: fp },
      messages
    };
  }

  /********************************************************************
   * SHARDING + DOWNLOAD
   ********************************************************************/
  function shardString(str, maxBytes) {
    // JS strings are UTF-16; approximate bytes via Blob for correctness
    const blob = new Blob([str], { type: "application/json" });
    if (blob.size <= maxBytes) return [str];

    // conservative slice: binary search chunk boundaries by substring length
    const shards = [];
    let start = 0;
    while (start < str.length) {
      let lo = start + 1;
      let hi = str.length;
      let best = lo;

      while (lo <= hi) {
        const mid = (lo + hi) >> 1;
        const b = new Blob([str.slice(start, mid)], { type: "application/json" }).size;
        if (b <= maxBytes) { best = mid; lo = mid + 1; }
        else { hi = mid - 1; }
      }

      shards.push(str.slice(start, best));
      start = best;
    }
    return shards;
  }

  function gmDownloadText(text, filename) {
    const blob = new Blob([text], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    try {
      GM_download({ url, name: filename, saveAs: CFG.saveAs });
    } catch (e) {
      throw new DownloadError("GM_download failed", { filename, err: String(e) });
    }
  }

  function safeName(s) {
    return (s || "").replace(/[^a-zA-Z0-9._-]+/g, "_").slice(0, 140);
  }

  function downloadChatArtifacts(runId, url, artifactObj) {
    const convoId = convoIdFromUrl(url) || "unknown";
    const baseName = `${CFG.exportPrefix}_${safeName(runId)}_chat_${safeName(convoId)}`;

    const json = JSON.stringify(artifactObj, null, 2);
    const shards = shardString(json, CFG.shardMaxBytes);

    const shardFiles = [];
    for (let i = 0; i < shards.length; i++) {
      const fn = (shards.length === 1)
        ? `${baseName}.json`
        : `${baseName}.part_${String(i + 1).padStart(4, "0")}.json`;
      gmDownloadText(shards[i], fn);
      shardFiles.push(fn);
    }
    return shardFiles;
  }

  function buildRunManifest() {
    const chats = [];
    for (const u of STATE.links) {
      const rec = STATE.chats[u];
      if (!rec) continue;
      chats.push({
        url: u,
        convoId: rec.convoId,
        status: rec.status,
        retries: rec.retries || 0,
        messageCount: rec.messageCount,
        fingerprint: rec.fingerprint,
        shards: rec.shards || [],
        error: rec.error || null,
      });
    }
    return {
      schema: "metablooms.run.manifest.vnext",
      exportedAt: nowIso(),
      runId: STATE.runId,
      startedAt: STATE.startedAt,
      finishedAt: nowIso(),
      total: STATE.links.length,
      completed: chats.filter(c => c.status === "DONE").length,
      skipped: chats.filter(c => c.status === "SKIP").length,
      failed: chats.filter(c => c.status === "FAIL").length,
      chats
    };
  }

  function downloadManifest() {
    if (!STATE.runManifest) throw new FailClosedError("No manifest available (run not finished)", {});
    const text = JSON.stringify(STATE.runManifest, null, 2);
    gmDownloadText(text, `${CFG.exportPrefix}_${safeName(STATE.runId)}_RUN_MANIFEST.json`);
    emit("DOWNLOAD_MANIFEST", { runId: STATE.runId });
  }

  function downloadTelemetry() {
    const payload = JSON.stringify({ exportedAt: nowIso(), telemetry: STATE.telemetry }, null, 2);
    gmDownloadText(payload, `${CFG.exportPrefix}_${safeName(STATE.runId || "no_run")}_TELEMETRY.json`);
    emit("DOWNLOAD_TELEMETRY", {});
  }

  /********************************************************************
   * PIPELINE
   ********************************************************************/
  function newRunId() {
    return "mbxv5_" + Math.random().toString(16).slice(2) + "_" + Date.now();
  }

  function startRun() {
    try {
      assertSessionOk();
      if (STATE.running) return;

      STATE.createdAt = STATE.createdAt || nowIso();
      STATE.startedAt = nowIso();
      STATE.lastProgressAt = Date.now();
      STATE.runId = STATE.runId || newRunId();
      STATE.running = true;
      STATE.pausedReason = null;
      STATE.phase = "ENUM_LINKS";
      STATE.links = [];
      STATE.index = 0;
      STATE.chats = {};
      STATE.runManifest = null;

      saveState();
      emit("START", { runId: STATE.runId, url: location.href });
      logLine(`START runId=${STATE.runId}`);
      uiStatus("Starting…");
    } catch (e) {
      const c = classifyError(e);
      emit("START_FAIL", { error: c.type, msg: e.message, meta: e.meta || {} });
      logLine(`START_FAIL ${c.type}: ${e.message}`);
      pauseRun(c.type);
    }
  }

  function requestStop() {
    STATE.running = false;
    STATE.phase = "STOPPED";
    saveState();
    emit("STOP_REQUESTED", {});
    uiStatus("Stopped.");
    logLine("STOP requested.");
  }

  function pauseRun(reason) {
    STATE.running = false;
    STATE.phase = "PAUSED";
    STATE.pausedReason = reason || "PAUSED";
    saveState();
    emit("PAUSED", { reason: STATE.pausedReason });
    uiStatus(`Paused: ${STATE.pausedReason}`);
  }

  async function processOneChat(url) {
    const rec = STATE.chats[url] || { status: "NEW", retries: 0, convoId: convoIdFromUrl(url) || null, shards: [] };
    STATE.chats[url] = rec;

    rec.status = "IN_PROGRESS";
    saveState();

    await gotoUrl(url);
    await waitStable(CFG.settleMs);

    const stabilized = await forceFullHistoryLoadFailClosed();
    const artifact = buildChatArtifact(url, stabilized);
    const shards = downloadChatArtifacts(STATE.runId, url, artifact);

    rec.status = "DONE";
    rec.convoId = artifact.convoId;
    rec.messageCount = artifact.extracted.messageCount;
    rec.fingerprint = artifact.extracted.digest;
    rec.shards = shards;
    rec.error = null;

    STATE.lastProgressAt = Date.now();
    saveState();

    emit("CHAT_DONE", { url, convoId: rec.convoId, messages: rec.messageCount, shards: shards.length });
    logLine(`DONE chat=${rec.convoId} msgs=${rec.messageCount} shards=${shards.length}`);
  }

  async function tick() {
    assertSessionOk();

    if (!STATE.running) return;

    if (Date.now() - (STATE.lastProgressAt || Date.now()) > 30_000) {
      emit("WATCHDOG", { idleMs: Date.now() - STATE.lastProgressAt });
      STATE.lastProgressAt = Date.now();
      saveState();
    }

    if ((Date.now() - new Date(STATE.startedAt || nowIso()).getTime()) > CFG.maxRuntimeMs) {
      emit("STOP_MAX_RUNTIME", {});
      STATE.running = false;
      STATE.phase = "STOPPED";
      saveState();
      return;
    }

    if (STATE.phase === "ENUM_LINKS") {
      uiStatus("Enumerating project conversation links…");
      logLine("Enumerating links (fail-closed on suspiciously low count) …");
      const links = await enumerateAllLinksFailClosed();
      STATE.links = links;
      STATE.index = 0;
      STATE.phase = "PROCESS_CHAT";
      saveState();
      emit("ENUM_DONE", { count: links.length });
      logLine(`ENUM_DONE count=${links.length}`);
      return;
    }

    if (STATE.phase === "PROCESS_CHAT") {
      if (STATE.index >= STATE.links.length) {
        STATE.running = false;
        STATE.phase = "STOPPED";
        STATE.runManifest = buildRunManifest();
        saveState();
        emit("RUN_DONE", { total: STATE.links.length });
        uiStatus("Run complete. Manifest ready.");
        logLine("RUN_DONE (manifest ready).");
        return;
      }

      const url = STATE.links[STATE.index];
      const rec = STATE.chats[url] || { status: "NEW", retries: 0, convoId: convoIdFromUrl(url) || null, shards: [] };
      STATE.chats[url] = rec;

      // skip already-done
      if (rec.status === "DONE") {
        STATE.index++;
        saveState();
        return;
      }

      uiStatus(`Processing ${STATE.index + 1}/${STATE.links.length}`);
      try {
        await processOneChat(url);
        STATE.index++;
        saveState();
      } catch (e) {
        const c = classifyError(e);
        rec.retries = (rec.retries || 0) + 1;
        rec.error = `${c.type}: ${e.message}`;
        emit("CHAT_FAIL", { url, error: c.type, msg: e.message, retries: rec.retries, meta: e.meta || {} });
        logLine(`FAIL chat url=${url} ${c.type}: ${e.message} (retry ${rec.retries}/${CFG.maxRetriesPerChat})`);

        if (c.terminal) {
          rec.status = "FAIL";
          saveState();
          pauseRun(c.type);
          return;
        }

        if (rec.retries >= CFG.maxRetriesPerChat) {
          rec.status = "SKIP";
          emit("CHAT_SKIP", { url, reason: c.type });
          logLine(`SKIP chat url=${url} reason=${c.type}`);
          STATE.index++;
        } else {
          rec.status = "NEW";
          // small backoff
          await sleep(900);
        }
        saveState();
      }
      return;
    }
  }

  async function mainLoop() {
    registerMenu();
    ensureUI();
    refreshUI();

    emit("BOOT", { url: location.href, host: location.host });

    while (true) {
      try {
        await tick();
      } catch (e) {
        const c = classifyError(e);
        emit("UNCAUGHT", { error: c.type, msg: e.message, meta: e.meta || {} });
        logLine(`UNCAUGHT ${c.type}: ${e.message}`);
        if (c.terminal) pauseRun(c.type);
        else await sleep(600);
      }
      await sleep(CFG.tickMs);
    }
  }

  // Start
  mainLoop();

})();
