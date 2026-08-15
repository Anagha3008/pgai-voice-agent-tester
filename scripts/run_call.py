import argparse

from app.call_service import create_outbound_call
from app.config import PG_TEST_NUMBER
from app.scenario_loader import get_scenario


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Start one PGAI assessment call."
    )
    parser.add_argument(
        "scenario_id",
        help="Scenario ID such as call-01.",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Required to place the real billable call.",
    )

    arguments = parser.parse_args()
    scenario = get_scenario(arguments.scenario_id)

    print(f"Scenario: {scenario['id']}")
    print(f"Objective: {scenario['objective']}")
    print(f"Destination: {PG_TEST_NUMBER}")

    if not arguments.confirm:
        print(
            "\nPreview only. No call was placed."
        )
        print(
            "Add --confirm only when ready for a real call."
        )
        return

    call_sid = create_outbound_call(
        arguments.scenario_id
    )

    print(f"Call started successfully: {call_sid}")


if __name__ == "__main__":
    main()