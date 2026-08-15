import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "reports" / "call_manifest.json"


def load_call_manifest() -> list[dict[str, Any]]:
    """Load the saved call manifest, or return an empty list."""

    if not MANIFEST_PATH.exists():
        return []

    return json.loads(
        MANIFEST_PATH.read_text(encoding="utf-8"),
    )


def save_call_manifest(entries: list[dict[str, Any]]) -> None:
    """Persist the call manifest used for batch downloads."""

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(entries, indent=2),
        encoding="utf-8",
    )


def append_call_result(
    scenario_id: str,
    call_sid: str,
    status: str,
) -> None:
    """Append one completed call to the manifest."""

    entries = load_call_manifest()
    entries.append(
        {
            "scenario_id": scenario_id,
            "call_sid": call_sid,
            "status": status,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    save_call_manifest(entries)
