#!/usr/bin/env python3
"""Render MBML/MPP tracker markdown from BTS ledger.
Usage:
  render_tracker.py <bts_ledger.ndjson> <tracker_spec.json> <out_md>
"""
import json, sys, time

def load_events(path):
    events=[]
    with open(path,"r",encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: continue
            try:
                events.append(json.loads(line))
            except Exception:
                continue
    return events

def seen_phrase(ev, phrases):
    # check phase and payload values as strings
    ph = str(ev.get("phase",""))
    payload = ev.get("payload",{})
    blob = ph + " " + json.dumps(payload, ensure_ascii=False)
    return any(p in blob for p in phrases)

def main():
    if len(sys.argv) < 4:
        print("USAGE: render_tracker.py <bts.ndjson> <spec.json> <out.md>", file=sys.stderr)
        return 2
    bts=sys.argv[1]; specp=sys.argv[2]; out=sys.argv[3]
    spec=json.load(open(specp,"r",encoding="utf-8"))
    events=load_events(bts)
    recent=events[-spec["rendering"].get("show_recent_events",8):]

    # compute done status by scanning all events
    def is_done(item):
        phrases=item.get("done_when",[])
        return any(seen_phrase(ev, phrases) for ev in events)

    phases=spec["phases"]
    milestones=spec.get("milestones",[])

    # active = first not-done phase in order
    active_phase=None
    for p in phases:
        if not is_done(p):
            active_phase=p["id"]
            break

    lines=[]
    lines.append(f"# MBML / MPP Progress Tracker")
    lines.append(f"- Generated: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    lines.append("")

    lines.append("## MPP Phases")
    for p in phases:
        done=is_done(p)
        box="☑" if done else "☐"
        label=f"{p['id']} {p['label']}"
        if p["id"]==active_phase:
            label=f"**{label}**"
        if done:
            label=f"~~{label}~~"
        lines.append(f"- {box} {label}")
    lines.append("")

    lines.append("## Build Milestones")
    active_m=None
    for m in milestones:
        if not is_done(m):
            active_m=m["id"]
            break
    for m in milestones:
        done=is_done(m)
        box="☑" if done else "☐"
        label=f"{m['id']} {m['label']}"
        if m["id"]==active_m:
            label=f"**{label}**"
        if done:
            label=f"~~{label}~~"
        lines.append(f"- {box} {label}")
    lines.append("")

    lines.append("## Recent BTS Events")
    for ev in recent:
        ts=ev.get("ts","")
        ph=ev.get("phase","")
        lines.append(f"- `{ts}` **{ph}**")
    lines.append("")

    with open(out,"w",encoding="utf-8") as f:
        f.write("\n".join(lines))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
