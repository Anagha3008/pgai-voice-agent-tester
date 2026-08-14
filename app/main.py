from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.responses import Response
from twilio.twiml.voice_response import Connect, VoiceResponse

from app.media_bridge import handle_media_stream
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
    """Return TwiML that connects a call to the audio WebSocket."""
    try:
        get_scenario(scenario_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    websocket_url = str(request.base_url).replace(
        "http://",
        "ws://",
    ).replace(
        "https://",
        "wss://",
    )
    websocket_url = f"{websocket_url}media-stream"

    response = VoiceResponse()
    connect = Connect()
    stream = connect.stream(url=websocket_url)
    stream.parameter(name="scenario_id", value=scenario_id)
    response.append(connect)

    return Response(
        content=str(response),
        media_type="application/xml",
    )


@app.websocket("/media-stream")
async def media_stream(websocket: WebSocket) -> None:
    """Connect Twilio's audio stream to OpenAI Realtime."""
    await handle_media_stream(websocket)