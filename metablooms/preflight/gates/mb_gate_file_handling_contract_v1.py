"""
FILE_HANDLING_CONTRACT_V1 — P0 Gate
"""

class FileHandlingContractGateV1:
    GATE_ID = "GATE.P0.FILE_HANDLING_CONTRACT.V1"

    def evaluate(self, context: dict) -> dict:
        intent = context.get("intent", "")
        artifacts = context.get("artifacts", {})
        claims = context.get("claims", [])

        if intent in ("SHIP_OS", "BOOT_OS"):
            if not artifacts.get("is_whole_os", False):
                return {
                    "pass": False,
                    "severity": "P0",
                    "reason": "NOT_WHOLE_OS",
                }

        missing = [c for c in claims if not artifacts.get("files", {}).get(c)]
        if missing:
            return {
                "pass": False,
                "severity": "P0",
                "reason": "UNMATERIALIZED_IMPROVEMENTS",
                "missing": missing,
            }

        return {"pass": True}
