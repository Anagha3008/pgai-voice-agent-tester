# Pretty Good AI Voice Agent Bug Report

## Test summary

- Test destination: `+18054398008`
- Caller number: Documented privately in the submission form
- Total completed calls: 0/10
- Test period: To be completed
- Overall result: Pending live testing

All patients, dates of birth, medications, and scenarios used in this
assessment are fictional.

## Severity definitions

- **Critical:** Creates immediate patient-safety, privacy, or security risk.
- **High:** Causes an incorrect clinical or operational outcome.
- **Medium:** Significantly confuses the caller or prevents task completion.
- **Low:** Minor conversational or usability issue.

## Call tracking

| Call | Scenario | Recording | Transcript | Result | Bugs |
|---|---|---|---|---|---|
| call-01 | Appointment scheduling | Pending | Pending | Pending | Pending |
| call-02 | Appointment rescheduling | Pending | Pending | Pending | Pending |
| call-03 | Appointment cancellation | Pending | Pending | Pending | Pending |
| call-04 | Medication refill | Pending | Pending | Pending | Pending |
| call-05 | Office hours and location | Pending | Pending | Pending | Pending |
| call-06 | Insurance question | Pending | Pending | Pending | Pending |
| call-07 | Closed-hours edge case | Pending | Pending | Pending | Pending |
| call-08 | Ambiguous request | Pending | Pending | Pending | Pending |
| call-09 | Interruption and barge-in | Pending | Pending | Pending | Pending |
| call-10 | Urgent-symptom safety | Pending | Pending | Pending | Pending |

## Findings

Add only issues supported by a transcript and recording.

### BUG-001 — Replace with concise issue title

- **Severity:** Critical / High / Medium / Low
- **Call:** `call-XX`
- **Transcript:** `transcripts/filename.txt`
- **Recording:** `recordings/filename.mp3`
- **Timestamp:** `MM:SS`
- **Scenario objective:** Describe what the patient bot was trying to accomplish.

**What happened**

Describe the agent’s actual response and behavior.

**Why this is a problem**

Explain the patient, safety, operational, or conversational impact.

**Expected behavior**

Explain what the agent should have done instead.

**Reproduction steps**

1. Run the stated scenario.
2. Observe the conversation at the specified timestamp.
3. Compare the response with the expected behavior.

**Evidence**

Include a short transcript excerpt. Do not include unnecessary personal
information.

## Positive observations

Record behaviors that worked particularly well, such as:

- Natural turn-taking
- Accurate confirmation
- Appropriate clarification questions
- Safe escalation
- Successful recovery after interruption

## Testing limitations

Document any limitations encountered during testing, such as telephony
latency, trial-account restrictions, transcription uncertainty, or
incomplete calls.