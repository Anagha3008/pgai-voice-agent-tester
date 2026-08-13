from fastapi import FastAPI

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