import os
import sys
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

# 1. Import your custom router
from alien_agent.agent import router as alien_router

load_dotenv()

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure ai_server/ is importable
if AGENT_DIR not in sys.path:
    sys.path.insert(0, AGENT_DIR)

# 2. Initialize the ADK App
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    allow_origins=["*"],
    web=True,
)

# 3. Include your router (This adds /alien/chat and /alien/get)
app.include_router(alien_router)

# --- Keep your helper endpoints ---

@app.get("/ping")
async def ping():
    return {"message": "yay :D"}

@app.get("/health")
async def health():
    return {"status": "ok"}

# --- Removed the messy run-alien logic ---

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)