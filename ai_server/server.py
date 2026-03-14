import os
import sys
import json
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.adk.cli.fast_api import get_fast_api_app

load_dotenv()

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYER_ID = "mcdiggity"

# Ensure ai_server/ is always importable (alien_generator.py lives here)
if AGENT_DIR not in sys.path:
    sys.path.insert(0, AGENT_DIR)

app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    allow_origins=["*"],
    web=True,
)


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    return text.strip()


class QARequest(BaseModel):
    session_id: str
    question: str
    answer: str


class AlienRequest(BaseModel):
    session_id: str
    alien_dialog: str
    turn_summary: str


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
    try:
        from alien_generator import AlienGenerator
        gen       = AlienGenerator()
        name      = gen.get_random_name()
        mood      = gen.get_random_mood()
        mbti      = gen.get_random_mbti()
        situation = gen.get_random_market_booth()
        greeting  = gen.get_random_greeting()
        likes     = gen.get_random_likes()
        dislikes  = gen.get_random_dislikes(likes)

        liked_words  = {w.split()[-1]: 5  for w in likes}
        banned_words = {w.split()[-1]: -3 for w in dislikes}

        return {
            "name": name, "mood": mood, "mbti": mbti,
            "situation": situation, "greeting": greeting,
            "likes": likes, "dislikes": dislikes,
            "liked_words": liked_words, "banned_words": banned_words,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run-qa")
async def run_qa(req: QARequest):
    import importlib
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types as genai_types

    try:
        qa_path = os.path.join(AGENT_DIR, "qa_agent")
        if qa_path not in sys.path:
            sys.path.insert(0, qa_path)

        if "agent" in sys.modules:
            del sys.modules["agent"]
        qa_mod = importlib.import_module("agent")
        agent  = qa_mod.root_agent

        svc    = InMemorySessionService()
        runner = Runner(agent=agent, app_name="qa_agent", session_service=svc)

        try:
            svc.get_session(app_name="qa_agent", user_id=PLAYER_ID,
                            session_id=req.session_id)
        except Exception:
            svc.create_session(app_name="qa_agent", user_id=PLAYER_ID,
                               session_id=req.session_id)

        msg = f'{{"question": {json.dumps(req.question)}}}\n{{"answer": {json.dumps(req.answer)}}}'
        content = genai_types.Content(
            role="user", parts=[genai_types.Part(text=msg)]
        )

        raw = ""
        for event in runner.run(user_id=PLAYER_ID,
                                session_id=req.session_id,
                                new_message=content):
            if event.is_final_response():
                raw = event.content.parts[0].text
                break

        return json.loads(_strip_fences(raw))

    except Exception as e:
        return {"validity": False, "reason": str(e), "summary": ""}


@app.post("/run-alien")
async def run_alien(req: AlienRequest):
    import importlib
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types as genai_types

    try:
        alien_path = os.path.join(AGENT_DIR, "alien_agent")
        if alien_path not in sys.path:
            sys.path.insert(0, alien_path)

        if "agent" in sys.modules:
            del sys.modules["agent"]
        alien_mod = importlib.import_module("agent")
        agent     = alien_mod.root_agent

        svc    = InMemorySessionService()
        runner = Runner(agent=agent, app_name="alien_agent", session_service=svc)

        try:
            svc.get_session(app_name="alien_agent", user_id=PLAYER_ID,
                            session_id=req.session_id)
        except Exception:
            svc.create_session(app_name="alien_agent", user_id=PLAYER_ID,
                               session_id=req.session_id)

        msg = (f'{{"alien_dialog": {json.dumps(req.alien_dialog)}}}\n'
               f'{{"turn_summary": {json.dumps(req.turn_summary)}}}')
        content = genai_types.Content(
            role="user", parts=[genai_types.Part(text=msg)]
        )

        raw = ""
        for event in runner.run(user_id=PLAYER_ID,
                                session_id=req.session_id,
                                new_message=content):
            if event.is_final_response():
                raw = event.content.parts[0].text
                break

        return {"reply": raw}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)