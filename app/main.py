from fastapi import FastAPI
from pydantic import BaseModel
import httpx

app = FastAPI()

class AgentRequest(BaseModel):
    message: str

@app.post("/agent")
def agent(req: AgentRequest):
    ollama_url = "http://host.docker.internal:11434/api/generate"
    payload = {
        "model": "llama3",
        "prompt": req.message,
        "stream": False
    }

    r = httpx.post(ollama_url, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()

    return {"reply": data["response"]}
