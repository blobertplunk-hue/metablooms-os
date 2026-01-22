from pathlib import Path
import json
from datetime import datetime
import uuid

OS_ROOT = Path("/mnt/data/MetaBlooms_OS")

def write_boot_receipt(turn_id: str, boot_mode: str):
    d = OS_ROOT / "ledgers" / "turns" / turn_id
    d.mkdir(parents=True, exist_ok=True)
    receipt = {
        "receipt_type": "TURN_BOOT_RECEIPT",
        "turn_id": turn_id,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "boot_mode": boot_mode,
        "state_mode": "FRESH_LOAD",
        "invariants_loaded": [
            "TURN_LOCAL_REHYDRATION",
            "EXECUTION_CLAIMS_ARE_TURN_LOCAL",
            "CANONICAL_BOOT_DISCOVERY",
            "AUTO_REHYDRATE_EVERY_TURN"
        ]
    }
    (d / "boot_receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return d / "boot_receipt.json"

def main():
    # Turn 1: boot only (no prior receipt required)
    t1 = "TURN_PROOF_" + datetime.utcnow().strftime("%Y%m%d_%H%M%S") + "_A"
    r1 = write_boot_receipt(t1, "INITIAL")

    # Turn 2: auto-rehydrate must succeed using Turn 1 receipt, then boot
    from metablooms.runtime.auto_rehydrate import auto_rehydrate
    t2 = "TURN_PROOF_" + datetime.utcnow().strftime("%Y%m%d_%H%M%S") + "_B"
    reh = auto_rehydrate(OS_ROOT, t2)  # writes rehydrate_receipt.json in t2 dir
    r2 = write_boot_receipt(t2, "CONTINUING")

    out = {
        "turn1_boot_receipt": str(r1),
        "turn2_rehydrate_receipt": str(OS_ROOT / "ledgers" / "turns" / t2 / "rehydrate_receipt.json"),
        "turn2_boot_receipt": str(r2),
        "rehydrate_receipt": reh
    }
    report = OS_ROOT / "ledgers" / "turns" / t2 / "PROOF_REPORT.json"
    report.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
