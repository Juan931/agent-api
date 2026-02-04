from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class AgentRequest(BaseModel):
    message: str
    
@app.post("/agent")
def agent(req: AgentRequest):
    return {"reply": f"OK: {req.message}"}