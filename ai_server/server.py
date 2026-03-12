import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

load_dotenv()

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_DB_URL = f"sqlite:///{os.path.join(AGENT_DIR, 'sessions.db')}"

app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_service_uri=SESSION_DB_URL, 
    allow_origins=["*"],
    web=True,
)

@app.get("/ping")
async def root():
    return {"message": "yay :D"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/agents")
async def list_agents():
    """Confirms which agents are available."""
    return {
        "agents": [
            "alien_agent",
            "qa_agent",
        ]
    }

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)