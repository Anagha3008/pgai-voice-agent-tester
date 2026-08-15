import argparse
import time

from app.call_manifest import append_call_result
from app.call_service import (
    create_outbound_call,
    wait_for_call_completion,
)
from app.config import PG_TEST_NUMBER
from app.scenario_loader import load_scenarios
from scripts.download_recordings import download_call_recordings


def download_with_retries(
    call_sid: str,
    scenario_id: str,
    attempts: int = 12,
    delay_seconds: int = 10,
) -> list[Path]:
    """Retry recording downloads until Twilio finishes processing."""

    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            return download_call_recordings(
                call_sid=call_sid,
                scenario_id=scenario_id,
            )
        except ValueError as error:
            last_error = error
            print(
                f"Recording not ready yet for {call_sid} "
                f"(attempt {attempt}/{attempts})."
            )
            time.sleep(delay_seconds)

    raise ValueError(
        f"Could not download recording for {call_sid}: {last_error}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run all PGAI assessment scenarios in sequence."
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Required to place real billable calls.",
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=30,
        help="Seconds to wait between calls (default: 30).",
    )
    parser.add_argument(
        "--start",
        default="call-01",
        help="Scenario ID to start from (default: call-01).",
    )
    parser.add_argument(
        "--download-recordings",
        action="store_true",
        help="Download each recording after the call completes.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Max seconds to wait for each call to finish (default: 300).",
    )

    arguments = parser.parse_args()
    scenarios = load_scenarios()
    started = False
    call_results: list[tuple[str, str, str]] = []

    print(f"Destination: {PG_TEST_NUMBER}")
    print(f"Scenarios: {len(scenarios)}")

    for scenario in scenarios:
        scenario_id = scenario["id"]

        if not started:
            if scenario_id != arguments.start:
                continue

            started = True

        print(f"\n--- {scenario_id}: {scenario['objective']} ---")

        if not arguments.confirm:
            print("Preview only. No call was placed.")
            continue

        call_sid = create_outbound_call(scenario_id)
        print(f"Call started: {call_sid}")
        print("Waiting for the call to finish...")

        status = wait_for_call_completion(
            call_sid,
            timeout_seconds=arguments.timeout,
        )
        append_call_result(scenario_id, call_sid, status)
        call_results.append((scenario_id, call_sid, status))
        print(f"Call finished with status: {status}")

        if arguments.download_recordings:
            print("Downloading recording...")
            paths = download_with_retries(call_sid, scenario_id)
            for path in paths:
                print(f"Saved recording: {path}")

        if scenario != scenarios[-1]:
            print(
                f"Waiting {arguments.delay} seconds before the next call..."
            )
            time.sleep(arguments.delay)

    if not arguments.confirm:
        print(
            "\nPreview only. Add --confirm when ready for real calls."
        )
        return

    if call_results:
        print("\nCompleted calls:")
        for scenario_id, call_sid, status in call_results:
            print(f"  {scenario_id}: {call_sid} ({status})")

        print(
            "\nManifest saved to reports/call_manifest.json"
        )

        if not arguments.download_recordings:
            print(
                "Download all recordings later with:\n"
                "  python -m scripts.download_all_recordings"
            )


if __name__ == "__main__":
    main()
