import argparse
import time

from app.call_manifest import load_call_manifest
from scripts.download_recordings import download_call_recordings


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download recordings for every call in the manifest."
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=10,
        help="Seconds to wait between download attempts (default: 10).",
    )
    parser.add_argument(
        "--attempts",
        type=int,
        default=12,
        help="Retry attempts per call (default: 12).",
    )

    arguments = parser.parse_args()
    manifest = load_call_manifest()

    if not manifest:
        raise SystemExit(
            "No calls found in reports/call_manifest.json. "
            "Run python -m scripts.run_all_calls --confirm first."
        )

    for entry in manifest:
        scenario_id = entry["scenario_id"]
        call_sid = entry["call_sid"]
        print(f"\nDownloading {scenario_id} ({call_sid})...")

        last_error: Exception | None = None

        for attempt in range(1, arguments.attempts + 1):
            try:
                paths = download_call_recordings(
                    call_sid=call_sid,
                    scenario_id=scenario_id,
                )
                for path in paths:
                    print(f"Saved recording: {path}")
                break
            except ValueError as error:
                last_error = error
                print(
                    f"Recording not ready yet "
                    f"(attempt {attempt}/{arguments.attempts})."
                )
                time.sleep(arguments.delay)
        else:
            raise SystemExit(
                f"Failed to download recording for {call_sid}: {last_error}"
            )

    print("\nAll manifest recordings downloaded.")


if __name__ == "__main__":
    main()
