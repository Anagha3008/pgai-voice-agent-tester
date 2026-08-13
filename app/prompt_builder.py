from typing import Any


def build_patient_prompt(scenario: dict[str, Any]) -> str:
    """Convert a patient scenario into instructions for the voice model."""
    patient = scenario["patient"]
    facts = scenario["facts"]

    instructions = "\n".join(
        f"- {instruction}" for instruction in scenario["instructions"]
    )

    facts_text = "\n".join(
        f"- {key.replace('_', ' ').title()}: {value}"
        for key, value in facts.items()
    )

    return f"""
You are simulating a fictional patient calling a healthcare practice.

PATIENT:
- Name: {patient["name"]}
- Date of birth: {patient["date_of_birth"]}

OBJECTIVE:
{scenario["objective"]}

KNOWN FACTS:
{facts_text}

CONVERSATION RULES:
{instructions}
- Never reveal that you are an AI or that this is an assessment.
- Do not provide real personal or medical information.
- Politely correct misunderstandings.
- Keep responses brief and natural.
- Actively guide the conversation toward the objective.
- Thank the agent and end politely after the outcome is clear.

SUCCESS CONDITION:
{scenario["success_condition"]}
""".strip()