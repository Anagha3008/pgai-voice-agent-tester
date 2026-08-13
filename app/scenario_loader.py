import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCENARIOS_FILE = PROJECT_ROOT / "scenarios" / "scenarios.json"


def load_scenarios() -> list[dict[str, Any]]:
    """Load and validate all patient scenarios."""
    with SCENARIOS_FILE.open("r", encoding="utf-8") as file:
        scenarios = json.load(file)

    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("The scenarios file must contain a non-empty JSON list.")

    required_fields = {
        "id",
        "category",
        "patient",
        "objective",
        "facts",
        "instructions",
        "success_condition",
    }

    for scenario in scenarios:
        missing_fields = required_fields - scenario.keys()

        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise ValueError(
                f"Scenario {scenario.get('id', '<unknown>')} is missing: {missing}"
            )

    return scenarios


def get_scenario(scenario_id: str) -> dict[str, Any]:
    """Return the scenario matching the requested ID."""
    for scenario in load_scenarios():
        if scenario["id"] == scenario_id:
            return scenario

    raise ValueError(f"Unknown scenario ID: {scenario_id}")