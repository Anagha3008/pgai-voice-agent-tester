# PGAI Voice Agent Tester — Submission Guide

This guide maps the assessment requirements to this repository.

## What is already in the repo

| Deliverable | Location |
|---|---|
| Working Python voice bot | `app/` |
| Setup and run instructions | `README.md` |
| Architecture doc | `ARCHITECTURE.md` |
| 10 patient scenarios | `scenarios/scenarios.json` |
| Bug report template | `reports/BUG_REPORT.md` |
| Environment template | `.env.example` |
| Automated tests | `tests/` |

## What you must complete manually

These cannot be generated without your API keys and live calls:

1. **10 real calls** to `+1-805-439-8008`
2. **Recordings** in `recordings/` (MP3)
3. **Transcripts** in `transcripts/` (auto-saved during calls)
4. **Bug report** filled in with real findings
5. **Two Loom videos** (public, webcam on):
   - Project walkthrough (max 3 minutes)
   - AI-assisted debugging session
6. **Public GitHub repo** link in the submission form
7. **Your Twilio caller number** in E.164 format in the form

## Recommended workflow

### 1. Explore the product

Create a test account at [pgai.us/athena](https://pgai.us/athena) to understand
the patient experience. Do not call the number on the confirmation screen.

### 2. Configure credentials

```bash
copy .env.example .env
```

Fill in OpenAI, Twilio, and your tunnel URL.

### 3. Start the server and tunnel

Terminal 1:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Terminal 2 (example with ngrok):

```bash
ngrok http 8000
```

Copy the HTTPS URL into `PUBLIC_BASE_URL` in `.env`.

### 4. Run all 10 calls

```bash
python -m scripts.run_all_calls --confirm --download-recordings
```

This will:

- Place each call to the assessment number only
- Wait for each call to finish before starting the next
- Save call metadata to `reports/call_manifest.json`
- Download MP3 recordings automatically

Transcripts are saved automatically during each call.

### 5. Review results

- Listen to recordings in `recordings/`
- Read transcripts in `transcripts/`
- Update `reports/BUG_REPORT.md` with evidence-backed bugs

Example bug entry:

```text
Bug: Agent confirms appointment for Sunday, but the practice is closed on weekends
Severity: High
Call: transcripts/call-07-CAxxxx.txt at 1:23
Details: When asked "Can I come in Sunday at 10am?", the agent scheduled
Sunday without checking office hours. Should have offered weekday alternatives.
```

### 6. Validate before submitting

```bash
python -m scripts.validate_submission
```

### 7. Record Loom videos

**Video 1 — Project walkthrough (max 3 min):**
- Show your face on camera
- Explain architecture choices (why OpenAI Realtime, Twilio, etc.)
- Demo one call and a bug you found
- Discuss tradeoffs you considered

**Video 2 — AI debugging session:**
- Screen record yourself using AI to fix a real bug
- Show the prompts you used at each step
- Explain how you iterated

### 8. Submit

Fill out the Pretty Good AI submission form with:

- Public GitHub repo URL
- Two public Loom video URLs
- Your Twilio caller number (E.164)
- Receipts for API/telephony costs (reimbursed up to $20)

## Cost expectations

Typical total cost is under $20 for OpenAI Realtime + Twilio usage across
10 calls. Keep receipts for reimbursement.

## Tips for passing call quality review

- Let the receptionist greet you first; the bot is prompted to wait
- Aim for 1–3 minute full conversations, not one-question hang-ups
- Use diverse scenarios already defined in `scenarios.json`
- Re-run a scenario if audio quality or turn-taking was poor
- Document both bugs and positive observations

## Iteration

After early calls, review transcripts and adjust scenario instructions in
`scenarios/scenarios.json` or patient prompts in `app/prompt_builder.py`
if conversations feel unnatural. Re-run specific scenarios:

```bash
python -m scripts.run_call call-07 --confirm
```
