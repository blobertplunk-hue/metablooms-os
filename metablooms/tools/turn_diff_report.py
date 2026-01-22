"""
MetaBlooms Turn-to-Turn Visual Diff Report
- Reads a diff JSON and emits:
    - Markdown summary report
    - Self-contained HTML report
Fail-closed:
    - If diff file missing/invalid -> exit(2)
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
from datetime import datetime

def _load_json(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        raise RuntimeError(f"JSON_LOAD_FAILED: {p}: {e}")

def _fmt_list(items):
    if not items:
        return "_(none)_"
    return "\n".join([f"- {x}" for x in items])

def emit_reports(diff_path: Path, out_dir: Path) -> tuple[Path, Path]:
    diff = _load_json(diff_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    meta = diff.get("meta", {})
    prev_turn = meta.get("prev_turn", "UNKNOWN_PREV")
    cur_turn  = meta.get("cur_turn", "UNKNOWN_CUR")
    created_utc = meta.get("created_utc", datetime.utcnow().isoformat() + "Z")

    added = diff.get("added", {})
    removed = diff.get("removed", {})
    changed = diff.get("changed", {})

    md = []
    md.append("# MetaBlooms Turn Diff Report")
    md.append(f"- Prev: `{prev_turn}`")
    md.append(f"- Cur: `{cur_turn}`")
    md.append(f"- Created: `{created_utc}`")
    md.append("")
    md.append("## Added")
    for k, v in added.items():
        md.append(f"### {k}")
        md.append(_fmt_list(v))
        md.append("")
    md.append("## Removed")
    for k, v in removed.items():
        md.append(f"### {k}")
        md.append(_fmt_list(v))
        md.append("")
    md.append("## Changed")
    for k, v in changed.items():
        md.append(f"### {k}")
        if not v:
            md.append("_(none)_\n")
            continue
        for item in v:
            before = item.get("before")
            after = item.get("after")
            key = item.get("key", "(unknown key)")
            md.append(f"- **{key}**: `{before}` → `{after}`")
        md.append("")

    md_path = out_dir / f"TURN_DIFF__{prev_turn}__{cur_turn}.md"
    md_path.write_text("\n".join(md), encoding="utf-8")

    def esc(s):
        return (str(s)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))

    html_sections = []
    html_sections.append("<h1>MetaBlooms Turn Diff Report</h1>")
    html_sections.append(f"<p><b>Prev</b>: {esc(prev_turn)}<br><b>Cur</b>: {esc(cur_turn)}<br><b>Created</b>: {esc(created_utc)}</p>")

    def render_block(title, obj):
        html_sections.append(f"<h2>{esc(title)}</h2>")
        if not obj:
            html_sections.append("<p><i>(none)</i></p>")
            return
        for k, v in obj.items():
            html_sections.append(f"<h3>{esc(k)}</h3>")
            if not v:
                html_sections.append("<p><i>(none)</i></p>")
            else:
                html_sections.append("<ul>" + "".join([f"<li>{esc(x)}</li>" for x in v]) + "</ul>")

    render_block("Added", added)
    render_block("Removed", removed)

    html_sections.append("<h2>Changed</h2>")
    if not changed:
        html_sections.append("<p><i>(none)</i></p>")
    else:
        for k, v in changed.items():
            html_sections.append(f"<h3>{esc(k)}</h3>")
            if not v:
                html_sections.append("<p><i>(none)</i></p>")
            else:
                html_sections.append("<ul>")
                for item in v:
                    key = item.get("key", "(unknown key)")
                    before = item.get("before")
                    after = item.get("after")
                    html_sections.append(f"<li><b>{esc(key)}</b>: <code>{esc(before)}</code> &rarr; <code>{esc(after)}</code></li>")
                html_sections.append("</ul>")

    html = (
        "<!doctype html><html><head><meta charset='utf-8'><title>MetaBlooms Turn Diff</title>"
        "<style>"
        "body{font-family:system-ui,Segoe UI,Roboto,Arial,sans-serif; margin:24px; line-height:1.35;}"
        "code{background:#f2f2f2; padding:2px 4px; border-radius:4px;}"
        "h1{margin-top:0}"
        "</style></head><body>"
        + "".join(html_sections) +
        "</body></html>"
    )
    html_path = out_dir / f"TURN_DIFF__{prev_turn}__{cur_turn}.html"
    html_path.write_text(html, encoding="utf-8")

    return md_path, html_path

def main(argv):
    if len(argv) < 3:
        print("USAGE: python -m metablooms.tools.turn_diff_report <diff_json> <out_dir>", file=sys.stderr)
        return 2
    diff_path = Path(argv[1])
    out_dir = Path(argv[2])
    if not diff_path.exists():
        print(f"DIFF_MISSING: {diff_path}", file=sys.stderr)
        return 2
    try:
        md_path, html_path = emit_reports(diff_path, out_dir)
    except Exception as e:
        print(f"REPORT_FAILED: {e}", file=sys.stderr)
        return 2
    print(f"REPORT_OK\nMD: {md_path}\nHTML: {html_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
