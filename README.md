# PGAI Voice Agent Tester

An automated Python voice bot for the Pretty Good AI engineering assessment.
It calls the official test line (`+1-805-439-8008`), simulates realistic
patient scenarios, records both sides of each conversation, and supports
evidence-based bug reporting.

For the full submission checklist, see [SUBMISSION.md](SUBMISSION.md).

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Fill in `.env`, then start the server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Expose port 8000 with ngrok or Cloudflare Tunnel and set `PUBLIC_BASE_URL`.

## Run all 10 assessment calls (single command)

After setup, place all calls, wait for completion, and download recordings:

```bash
python -m scripts.run_all_calls --confirm --download-recordings
```

Transcripts are saved automatically to `transcripts/` during each call.

## Safety

Outbound calls are permitted only to the official assessment number:

```text
+18054398008
```

## Prerequisites

- Python 3.11+
- [Twilio](https://www.twilio.com/) account with a phone number
- [OpenAI](https://platform.openai.com/) API key with Realtime access
- A public HTTPS tunnel ([ngrok](https://ngrok.com/) or [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/))

## Environment variables

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key |
| `TWILIO_ACCOUNT_SID` | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | Twilio auth token |
| `TWILIO_PHONE_NUMBER` | Your Twilio number in E.164 format |
| `PUBLIC_BASE_URL` | Public HTTPS tunnel URL (no trailing slash) |

## Step-by-step

### 1. Install

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
copy .env.example .env
```

### 2. Start server (terminal 1)

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Start tunnel (terminal 2)

```bash
ngrok http 8000
```

Copy the HTTPS URL into `PUBLIC_BASE_URL` in `.env`.

### 4. Preview a scenario (no call placed)

```bash
python -m scripts.run_call call-01
```

### 5. Place one call

```bash
python -m scripts.run_call call-01 --confirm
```

### 6. Run all 10 scenarios

```bash
python -m scripts.run_all_calls --confirm --download-recordings
```

### 7. Download recordings later (if needed)

```bash
python -m scripts.download_all_recordings
```

### 8. Validate submission artifacts

```bash
python -m scripts.validate_submission
```

### 9. Document bugs

Edit `reports/BUG_REPORT.md` with findings backed by transcript and
recording evidence.

## Scenarios

Ten fictional patient scenarios in `scenarios/scenarios.json`:

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

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md).

## Testing

```bash
pytest tests/ -v
```

## Project layout

```text
app/
  main.py                 FastAPI server and TwiML endpoints
  media_bridge.py         Twilio ↔ OpenAI audio relay and transcripts
  realtime_client.py      OpenAI Realtime session configuration
  call_service.py         Outbound call creation via Twilio
  call_manifest.py        Call tracking for batch downloads
  scenario_loader.py      Scenario JSON loading and validation
  prompt_builder.py       Patient persona prompt construction
scenarios/scenarios.json  Ten fictional patient scenarios
scripts/
  run_call.py             Place one call
  run_all_calls.py        Run all scenarios sequentially
  download_recordings.py  Download one recording
  download_all_recordings.py
  validate_submission.py
tests/
reports/
  BUG_REPORT.md           Evidence-based bug report
  call_manifest.json      Generated after running all calls
recordings/               Downloaded MP3 files
transcripts/              Auto-saved per-call transcripts
```

## Assessment deliverables checklist

- [ ] 10 completed calls with recordings and transcripts
- [ ] Bug report with evidence in `reports/BUG_REPORT.md`
- [ ] Public GitHub repository
- [ ] Loom walkthrough video (max 3 min, webcam on)
- [ ] Loom AI debugging video (screen recording)
- [ ] Submission form with repo link, videos, and caller number
