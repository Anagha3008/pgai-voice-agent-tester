from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from twilio.twiml.voice_response import Connect, VoiceResponse

from app.scenario_loader import get_scenario


app = FastAPI(
    title="PGAI Voice Agent Tester",
    description="Automated patient voice bot for healthcare-agent testing.",
    version="0.1.0",
)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "service": "PGAI Voice Agent Tester",
        "status": "running",
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.api_route("/outbound-call", methods=["GET", "POST"])
async def outbound_call(
    request: Request,
    scenario_id: str = "call-01",
) -> Response:
    """Return TwiML that connects a call to our audio WebSocket."""
    try:
        get_scenario(scenario_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    websocket_url = str(request.base_url).replace("http://", "ws://").replace(
        "https://", "wss://"
    )
    websocket_url = f"{websocket_url}media-stream"

    response = VoiceResponse()
    connect = Connect()
    stream = connect.stream(url=websocket_url)
    stream.parameter(name="scenario_id", value=scenario_id)
    response.append(connect)

    return Response(content=str(response), media_type="application/xml")


@app.websocket("/media-stream")
async def media_stream(websocket: WebSocket) -> None:
    """Receive live Twilio Media Stream events."""
    await websocket.accept()

    stream_sid: str | None = None
    scenario_id: str | None = None

    try:
        while True:
            message = await websocket.receive_json()
            event = message.get("event")

            if event == "connected":
                print("Twilio media connection established")

            elif event == "start":
                start_data = message.get("start", {})
                stream_sid = start_data.get("streamSid")

                custom_parameters = start_data.get("customParameters", {})
                scenario_id = custom_parameters.get("scenario_id", "call-01")

                get_scenario(scenario_id)

                print(f"Media stream started: {stream_sid}")
                print(f"Scenario selected: {scenario_id}")

            elif event == "media":
                # Audio forwarding to OpenAI will be added next.
                continue

            elif event == "stop":
                print(f"Media stream stopped: {stream_sid}")
                break

    except WebSocketDisconnect:
        print(f"Media stream disconnected: {stream_sid}")