# Architecture

The system uses Twilio Programmable Voice to place an outbound call from
one controlled caller number to the Pretty Good AI assessment number.
Twilio requests call instructions from the FastAPI `/outbound-call`
endpoint, which returns TwiML connecting the call to `/media-stream`.
A Cloudflare Tunnel exposes the local FastAPI server through HTTPS and
WSS. The WebSocket bridge forwards the practice agent's G.711 μ-law
audio from Twilio to OpenAI Realtime and streams the simulated patient's
generated audio back to Twilio. Each call loads a fictional patient
scenario from JSON and converts it into instructions that guide the
patient bot toward a specific testing objective.

I selected OpenAI Realtime instead of separate speech-to-text, language
model, and text-to-speech services because direct speech-to-speech
streaming reduces integration complexity and conversational latency.
The tradeoff is greater dependence on one realtime API and less direct
control over each audio-processing stage. Twilio dual-channel recording
preserves both sides of each conversation as reviewable evidence, while
Realtime transcript events create structured JSON and readable text
transcripts. Destination validation restricts calls to the assessment
number, secrets remain in an uncommitted `.env` file, and automated tests
cover destination safety, scenario loading, prompt construction,
transcript persistence, and recording downloads.