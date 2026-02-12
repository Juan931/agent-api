import os

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


# ---------- Models (request/response) ----------
class AgentRequest(BaseModel):
    message: str


class AgentResponse(BaseModel):
    reply: str


class HealthResponse(BaseModel):
    status: str


# ---------- Config (STRICT: required env vars) ----------
def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


OLLAMA_BASE_URL = require_env("OLLAMA_BASE_URL")          # e.g. http://host.docker.internal:11434
OLLAMA_MODEL = require_env("OLLAMA_MODEL")                # e.g. llama3
OLLAMA_NUM_PREDICT = int(require_env("OLLAMA_NUM_PREDICT"))  # e.g. 128


# ---------- Routes ----------
@app.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok"}


@app.post("/agent", response_model=AgentResponse)
def agent(req: AgentRequest):
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": req.message,
        "stream": False,
        "options": {"num_predict": OLLAMA_NUM_PREDICT},
    }

    try:
        r = httpx.post(url, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()

        # Ollama docs show "response" field for /api/generate responses [web:206]
        reply = data.get("response")
        if not isinstance(reply, str):
            raise HTTPException(status_code=502, detail="Ollama returned unexpected payload (missing 'response').")

        return {"reply": reply}

    except httpx.RequestError as e:
        # Network errors: cannot connect, DNS, timeout, etc.
        raise HTTPException(status_code=503, detail=f"Ollama unavailable (localhost:11434): {e}")  # [web:134]

    except httpx.HTTPStatusError as e:
        # Non-2xx response from Ollama
        raise HTTPException(
            status_code=502,
            detail=f"Ollama error {e.response.status_code}: {e.response.text}",
        )