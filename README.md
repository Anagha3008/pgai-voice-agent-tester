# PGAI Voice Agent Tester

An automated Python voice bot that calls the Pretty Good AI assessment
line and behaves like a fictional patient. It tests healthcare workflows,
records both sides of each conversation, creates transcripts, and supports
evidence-based bug reporting.

## Safety

The application permits outbound calls only to the official assessment
number:

```text
+18054398008
```

Any attempt to call another number is rejected at runtime.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full system design. In
short:

1. Twilio places an outbound call to the assessment number.
2. Twilio fetches TwiML from `/outbound-call` and connects to `/media-stream`.
3. A Cloudflare Tunnel or ngrok URL exposes the local FastAPI server over HTTPS/WSS.
4. The media bridge relays G.711 μ-law audio between Twilio and OpenAI Realtime.
5. Each call loads a fictional patient scenario and guides the patient bot.

## Prerequisites

- Python 3.11+
- [Twilio](https://www.twilio.com/) account with a phone number
- [OpenAI](https://platform.openai.com/) API key with Realtime access
- A public HTTPS tunnel ([Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) or [ngrok](https://ngrok.com/))

## Setup

1. Clone the repository and create a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

2. Copy the environment template and fill in your credentials:

```bash
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux
```

Required variables:

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key |
| `TWILIO_ACCOUNT_SID` | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | Twilio auth token |
| `TWILIO_PHONE_NUMBER` | Your Twilio number in E.164 format |
| `PUBLIC_BASE_URL` | Public HTTPS URL for your tunnel (no trailing slash) |

3. Start the FastAPI server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

4. Start your tunnel and set `PUBLIC_BASE_URL` to the tunnel URL.

## Running calls

Preview a scenario without placing a call:

```bash
python -m scripts.run_call call-01
```

Place a real call (billable):

```bash
python -m scripts.run_call call-01 --confirm
```

Run all 10 scenarios in sequence:

```bash
python -m scripts.run_all_calls --confirm
```

After a call completes, download the Twilio recording:

```bash
python -m scripts.download_recordings --call-sid CAxxxxxxxx --scenario-id call-01
```

## Scenarios

Ten fictional patient scenarios are defined in `scenarios/scenarios.json`:

| ID | Category |
|---|---|
| call-01 | Appointment scheduling |
| call-02 | Appointment rescheduling |
| call-03 | Appointment cancellation |
| call-04 | Medication refill |
| call-05 | Office hours and location |
| call-06 | Insurance question |
| call-07 | Closed-hours edge case |
| call-08 | Ambiguous request |
| call-09 | Interruption and barge-in |
| call-10 | Urgent-symptom safety |

Transcripts are saved automatically to `transcripts/` during each call.

## Testing

```bash
pytest tests/ -v
```

## Submission checklist

1. Run all 10 scenarios with `--confirm`.
2. Download recordings for each completed call.
3. Review transcripts in `transcripts/`.
4. Document findings in `reports/BUG_REPORT.md` with transcript and recording evidence.
5. Validate artifacts:

```bash
python -m scripts.validate_submission
```

## Project layout

```text
app/
  main.py              FastAPI server and TwiML endpoints
  media_bridge.py      Twilio ↔ OpenAI audio relay and transcripts
  realtime_client.py   OpenAI Realtime session configuration
  call_service.py      Outbound call creation via Twilio
  scenario_loader.py   Scenario JSON loading and validation
  prompt_builder.py    Patient persona prompt construction
scenarios/
  scenarios.json       Ten fictional patient scenarios
scripts/
  run_call.py          Place one call
  run_all_calls.py     Run all scenarios sequentially
  download_recordings.py
  validate_submission.py
tests/                 Automated safety and artifact tests
reports/
  BUG_REPORT.md        Evidence-based bug report template
recordings/            Downloaded call recordings (gitignored output)
transcripts/           Per-call transcripts (gitignored output)
```
