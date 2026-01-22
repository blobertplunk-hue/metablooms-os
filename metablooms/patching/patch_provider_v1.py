from typing import Any, Dict, Optional


def provide_patch(diagnosis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Patch provider interface.

    Contract:
      - input: diagnosis dict (evidence-backed)
      - output: patch_spec dict or None

    Patch spec (recommended minimal shape):
      {
        "patch_id": "...",
        "actions": [
          {"op": "replace_file", "path": "...", "content": "..."},
          {"op": "apply_unified_diff", "diff": "..."}
        ]
      }

    Note: MetaBlooms core can bind this to an LLM-backed implementation.
    This stub returns None to keep fail-closed behavior: if no patch, loop stops.
    """
    return None
