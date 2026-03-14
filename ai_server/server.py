import os
import json
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
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

# ── helpers ────────────────────────────────────────────────────────────────────

def _first_model_text(adk_response) -> str:
    """Pull the first model-role text part out of an ADK runner response."""
    if isinstance(adk_response, list):
        for event in adk_response:
            content = event.get("content", {})
            if content.get("role") == "model":
                for part in content.get("parts", []):
                    if "text" in part:
                        return part["text"]
    return ""


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    return text.strip()


# ── request models ─────────────────────────────────────────────────────────────

class QARequest(BaseModel):
    session_id: str
    question: str
    answer: str


class AlienRequest(BaseModel):
    session_id: str
    alien_dialog: str      # alien's latest line
    turn_summary: str      # QA summary of what the player said


# ── routes ─────────────────────────────────────────────────────────────────────

@app.get("/ping")
async def ping():
    return {"message": "yay :D"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/agents")
async def list_agents():
    return {"agents": ["alien_agent", "qa_agent"]}


@app.get("/generate-alien")
async def generate_alien():
    """
    Calls alien_generator directly (no ADK session needed) and returns a JSON
    dict describing the newly generated alien.
    """
    try:
        from alien_generator import AlienGenerator
        gen = AlienGenerator.__new__(AlienGenerator)  # skip __init__ print
        AlienGenerator.__init__(gen)

        name      = gen.get_random_name()
        mood      = gen.get_random_mood()
        mbti      = gen.get_random_mbti()
        situation = gen.get_random_market_booth()
        greeting  = gen.get_random_greeting()
        likes     = gen.get_random_likes()
        dislikes  = gen.get_random_dislikes(likes)

        # Build liked_words / banned_words from likes/dislikes for the point
        # calculator.  Values are intentionally small so turns matter.
        liked_words  = {w.split()[-1]: 5 for w in likes}
        banned_words = {w.split()[-1]: -3 for w in dislikes}

        return {
            "name":        name,
            "mood":        mood,
            "mbti":        mbti,
            "situation":   situation,
            "greeting":    greeting,
            "likes":       likes,
            "dislikes":    dislikes,
            "liked_words": liked_words,
            "banned_words": banned_words,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run-qa")
async def run_qa(req: QARequest):
    """
    Run the qa_agent synchronously and return a parsed JSON validity dict.
    Expected response shape: {"validity": bool, "reason": str, "summary": str}
    """
    from google.adk.runners import Runner
    from google.adk.sessions import DatabaseSessionService
    import importlib, sys

    try:
        # Dynamically load the qa_agent module
        qa_mod_path = os.path.join(AGENT_DIR, "qa_agent")
        if qa_mod_path not in sys.path:
            sys.path.insert(0, qa_mod_path)

        qa_mod = importlib.import_module("agent")
        agent  = qa_mod.root_agent

        svc     = DatabaseSessionService(SESSION_DB_URL)
        runner  = Runner(agent=agent, app_name="qa_agent", session_service=svc)
        session = svc.get_session(app_name="qa_agent", user_id="server",
                                  session_id=req.session_id)

        from google.genai import types as genai_types
        message = f'{{"question": "{req.question}"}}\n{{"answer": "{req.answer}"}}'
        content = genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=message)]
        )

        raw_text = ""
        for event in runner.run(user_id="server",
                                session_id=req.session_id,
                                new_message=content):
            if event.is_final_response():
                raw_text = event.content.parts[0].text
                break

        parsed = json.loads(_strip_fences(raw_text))
        return parsed

    except Exception as e:
        return {"validity": False, "reason": str(e), "summary": ""}


@app.post("/run-alien")
async def run_alien(req: AlienRequest):
    """
    Send the player's (QA-validated) turn summary to the alien_agent and get
    the alien's next dialogue line.
    Returns: {"reply": str}
    """
    from google.adk.runners import Runner
    from google.adk.sessions import DatabaseSessionService
    import importlib, sys

    try:
        alien_mod_path = os.path.join(AGENT_DIR, "alien_agent")
        if alien_mod_path not in sys.path:
            sys.path.insert(0, alien_mod_path)

        alien_mod = importlib.import_module("agent")
        agent     = alien_mod.root_agent

        svc    = DatabaseSessionService(SESSION_DB_URL)
        runner = Runner(agent=agent, app_name="alien_agent", session_service=svc)

        from google.genai import types as genai_types
        message = (f'{{"alien_dialog": "{req.alien_dialog}"}}\n'
                   f'{{"turn_summary": "{req.turn_summary}"}}')
        content = genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=message)]
        )

        raw_text = ""
        for event in runner.run(user_id=PLAYER_ID,
                                session_id=req.session_id,
                                new_message=content):
            if event.is_final_response():
                raw_text = event.content.parts[0].text
                break

        return {"reply": raw_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)