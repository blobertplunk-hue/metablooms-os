import os
import json
import hashlib
from datetime import datetime, timezone

def _canonical_bytes(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def _sha256_hex(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

class EvidencePack:
    def __init__(self, evidence_root: str, run_id: str, data: dict):
        self.evidence_root = evidence_root
        self.run_id = run_id
        self.data = data
        self.dir = os.path.join(evidence_root, "PROMOTION", run_id)
        os.makedirs(self.dir, exist_ok=True)

    @classmethod
    def begin(cls, evidence_root: str, run_id: str, parent_evidence_id: str | None,
              mode_requested: str | None, mode_effective: str,
              inputs: dict, ecl_gates_active: list[str], see_block: dict):
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        data = {
            "evidence_id": None,
            "parent_evidence_id": parent_evidence_id,
            "run_id": run_id,
            "run_kind": "PROMOTION",
            "timestamp": now,
            "mode": {"requested": mode_requested, "effective": mode_effective, "mdl": "MDL-0002"},
            "inputs": inputs,
            "mdl_registry": ["MDL-0001","MDL-0002","MDL-0003","MDL-0004","MDL-0005","MDL-0006"],
            "ecl_gates_active": ecl_gates_active,
            "see": see_block,
            "mmd": {"findings": [], "severity": "CLEAR"},
            "decision": None,
            "consequence": None,
            "recursion": None,
            "final_status": None
        }
        ep = cls(evidence_root, run_id, data)
        ep._write_json("evidence_pack.json", data)
        ep._write_md("evidence_pack.md", "IN-PROGRESS")
        return ep

    def set_mmd(self, mmd: dict):
        self.data["mmd"] = mmd

    def set_decision(self, decision: dict):
        self.data["decision"] = decision

    def set_consequence(self, consequence: dict):
        self.data["consequence"] = consequence
        if consequence.get("action") == "BLOCK":
            self.data["recursion"] = {
                "required": True,
                "reason": "Blocking MMD finding or gate failure",
                "next_actions": [
                    "Collect external documentation for dependent tool semantics",
                    "Attach at least one HIGH confidence primary source",
                    "Attach at least one MED+ corroborating source"
                ]
            }
        else:
            self.data["recursion"] = {"required": False, "note": "No blocking condition"}

    def finalize(self, final_status: str) -> str:
        self.data["final_status"] = final_status
        canon_obj = {k: v for k, v in self.data.items() if k != "evidence_id"}
        eid = _sha256_hex(_canonical_bytes(canon_obj))
        self.data["evidence_id"] = f"sha256:{eid}"
        self._write_json("evidence_pack.json", self.data)
        self._write_md("evidence_pack.md", self._render_md())
        return self.data["evidence_id"]

    def _write_json(self, name: str, obj: dict):
        with open(os.path.join(self.dir, name), "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)

    def _write_md(self, name: str, body: str):
        with open(os.path.join(self.dir, name), "w", encoding="utf-8") as f:
            f.write(body if body.endswith("\n") else body + "\n")

    def _render_md(self) -> str:
        status = self.data.get("final_status")
        decision = self.data.get("decision") or {}
        consequence = self.data.get("consequence") or {}
        see = self.data.get("see") or {}
        lines = [
            f"# Evidence Pack — {self.run_id}",
            "",
            f"**Status:** {status}",
            f"**Mode:** {self.data.get('mode', {}).get('effective')}",
            f"**Decision:** {decision.get('result')}",
            f"**Consequence:** {consequence.get('action')}",
        ]
        if consequence.get("reason_code"):
            lines.append(f"**Reason Code:** {consequence.get('reason_code')}")
        lines += [
            "",
            "## External SEE",
            f"- required: {see.get('external_required')}",
            f"- triggered_by: {see.get('external_triggered_by')}",
            f"- items: {len(see.get('external_items') or [])}",
            ""
        ]
        if decision.get("reasons"):
            lines.append("## Reasons")
            for r in decision["reasons"]:
                lines.append(f"- {r}")
            lines.append("")
        lines += [
            "## Lineage",
            f"- parent_evidence_id: {self.data.get('parent_evidence_id')}",
            f"- evidence_id: {self.data.get('evidence_id')}",
            ""
        ]
        return "\n".join(lines)
