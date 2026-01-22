METAGATE_ID = "METAGATE.P0.ARCHIVE.SINGLE_WRITER.V1"


def evaluate(context: dict):
    """Blocks direct archive writes unless component is Archive Manager."""
    component = context.get("component")
    path = context.get("target_path", "")

    if not component:
        return {"metagate_id": METAGATE_ID, "pass": False, "errors": ["MISSING_CONTEXT:component"]}

    # Only enforce when writing under archives namespace
    if "/archives/" not in path.replace("\\", "/"):
        return {"metagate_id": METAGATE_ID, "pass": True, "errors": []}

    if component != "archive_manager":
        return {"metagate_id": METAGATE_ID, "pass": False, "errors": ["ARCHIVE_SINGLE_WRITER_VIOLATION"]}

    return {"metagate_id": METAGATE_ID, "pass": True, "errors": []}
