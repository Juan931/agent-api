from fastapi import FastAPI
from pydantic import BaseModel
import os
import httpx

app = FastAPI()

class AgentRequest(BaseModel):
    message: str
    
def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value

OLLAMA_BASE_URL = require_env("OLLAMA_BASE_URL")          # e.g. http://host.docker.internal:11434
OLLAMA_MODEL = require_env("OLLAMA_MODEL")                # e.g. llama3
OLLAMA_NUM_PREDICT = int(require_env("OLLAMA_NUM_PREDICT"))  # e.g. 128

@app.post("/agent")
def agent(req: AgentRequest):
    url = f"{OLLAMA_BASE_URL}/api/generate"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": req.message,
        "stream": False,
        "options": {"num_predict": OLLAMA_NUM_PREDICT},
    }

    r = httpx.post(url, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()

    return {"reply": data["response"]}

