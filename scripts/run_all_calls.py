import argparse
import time

from app.call_service import create_outbound_call
from app.config import PG_TEST_NUMBER
from app.scenario_loader import load_scenarios


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
        default=90,
        help="Seconds to wait between calls (default: 90).",
    )
    parser.add_argument(
        "--start",
        default="call-01",
        help="Scenario ID to start from (default: call-01).",
    )

    arguments = parser.parse_args()
    scenarios = load_scenarios()
    started = False
    call_results: list[tuple[str, str]] = []

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
        call_results.append((scenario_id, call_sid))
        print(f"Call started: {call_sid}")
        print(
            "Download recording after the call completes:\n"
            f"  python -m scripts.download_recordings "
            f"--call-sid {call_sid} --scenario-id {scenario_id}"
        )

        if scenario != scenarios[-1]:
            print(f"Waiting {arguments.delay} seconds before the next call...")
            time.sleep(arguments.delay)

    if not arguments.confirm:
        print(
            "\nPreview only. Add --confirm when ready for real calls."
        )
        return

    if call_results:
        print("\nCompleted calls:")
        for scenario_id, call_sid in call_results:
            print(f"  {scenario_id}: {call_sid}")


if __name__ == "__main__":
    main()
