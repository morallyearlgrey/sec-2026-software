import os
import sys
import json
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.sessions import InMemorySessionService

load_dotenv()

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYER_ID = "mcdiggity"

# Ensure ai_server/ and alien_agent/ are always importable
alien_agent_path = os.path.join(AGENT_DIR, "alien_agent")
if AGENT_DIR not in sys.path:
    sys.path.insert(0, AGENT_DIR)
if alien_agent_path not in sys.path:
    sys.path.insert(0, alien_agent_path)

# Shared session services — must persist across requests
_qa_svc    = InMemorySessionService()
_alien_svc = InMemorySessionService()

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


def _unwrap_reply(raw: str) -> str:
    """If the agent echoed back a JSON object, extract the text value from it."""
    raw = raw.strip()
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict):
            for key in ("alien_dialog", "reply", "response", "message", "text"):
                if key in obj:
                    return str(obj[key])
            for v in obj.values():
                if isinstance(v, str):
                    return v
    except Exception:
        pass
    return raw


def _parse_qa_response(raw: str) -> dict:
    """Robustly parse QA agent response — handles JSON, fenced JSON, or plain text."""
    cleaned = _strip_fences(raw)
    # Try direct JSON parse
    try:
        result = json.loads(cleaned)
        if isinstance(result, dict) and "validity" in result:
            return result
    except Exception:
        pass
    # Try to find a JSON object inside the text
    try:
        start = cleaned.index("{")
        end   = cleaned.rindex("}") + 1
        result = json.loads(cleaned[start:end])
        if isinstance(result, dict) and "validity" in result:
            return result
    except Exception:
        pass
    # Fallback — treat whole response as a reason for failure
    return {"validity": False, "reason": raw[:200], "summary": ""}


class QARequest(BaseModel):
    session_id: str
    question: str
    answer: str


class AlienRequest(BaseModel):
    session_id: str
    alien_dialog: str
    turn_summary: str
    alien_prompt: str = ""


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

        prompt = (
            f"Your name is {name}. You are an alien. Your mood is {mood} and "
            f"you're an {mbti}. You work as a {situation[0]}, and you are situated in a "
            f"booth at a market where you are selling {situation[1]}. You enjoy {likes[0]}, "
            f"{likes[1]}, and {likes[2]}. You hate {dislikes[0]}, {dislikes[1]}, and "
            f"{dislikes[2]}. You have a maximum dialog of 5 responses before you want to end "
            f"the conversation. Your greeting is \"{greeting}\". Someone is looking to invite "
            f"you to the grand opening of their restaurant, but you don't know that yet. All "
            f"you know is that they approached your booth. "
            f"Always respond in plain conversational text. Never wrap your response in JSON."
        )

        return {
            "name": name, "mood": mood, "mbti": mbti,
            "situation": situation, "greeting": greeting,
            "likes": likes, "dislikes": dislikes,
            "liked_words": liked_words, "banned_words": banned_words,
            "prompt": prompt,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run-qa")
async def run_qa(req: QARequest):
    import importlib
    from google.adk.runners import Runner
    from google.genai import types as genai_types

    try:
        shared_path = os.path.join(AGENT_DIR, "shared")
        if shared_path not in sys.path:
            sys.path.insert(0, shared_path)
        qa_path = os.path.join(AGENT_DIR, "qa_agent")
        if qa_path not in sys.path:
            sys.path.insert(0, qa_path)

        if "agent" in sys.modules:
            del sys.modules["agent"]
        qa_mod = importlib.import_module("agent")
        agent  = qa_mod.root_agent

        runner = Runner(agent=agent, app_name="qa_agent", session_service=_qa_svc)

        existing = await _qa_svc.get_session(app_name="qa_agent", user_id=PLAYER_ID,
                                             session_id=req.session_id)
        if existing is None:
            await _qa_svc.create_session(app_name="qa_agent", user_id=PLAYER_ID,
                                         session_id=req.session_id)

        # Pass question and answer separately so prechecks tool gets just the answer
        msg = (
            f"Alien's question: {req.question}\n"
            f"Player's answer: {req.answer}\n\n"
            f"Call prechecks with the player's answer: {req.answer}"
        )
        content = genai_types.Content(
            role="user", parts=[genai_types.Part(text=msg)]
        )

        raw = ""
        async for event in runner.run_async(user_id=PLAYER_ID,
                                            session_id=req.session_id,
                                            new_message=content):
            if event.is_final_response() and event.content and event.content.parts:
                raw = event.content.parts[0].text or ""
                if raw:
                    break

        if not raw:
            return {"validity": False, "reason": "No response from QA agent", "summary": ""}

        return _parse_qa_response(raw)

    except Exception as e:
        return {"validity": False, "reason": str(e), "summary": ""}


@app.post("/run-alien")
async def run_alien(req: AlienRequest):
    from google.adk.runners import Runner
    from google.adk.agents import Agent
    from google.genai import types as genai_types

    try:
        if not req.alien_prompt:
            raise HTTPException(status_code=400, detail="alien_prompt is required")

        agent = Agent(
            name="alien_agent",
            model="gemini-2.5-flash",
            instruction=req.alien_prompt,
            tools=[],
        )

        runner = Runner(agent=agent, app_name="alien_agent", session_service=_alien_svc)

        existing = await _alien_svc.get_session(app_name="alien_agent", user_id=PLAYER_ID,
                                                session_id=req.session_id)
        if existing is None:
            await _alien_svc.create_session(app_name="alien_agent", user_id=PLAYER_ID,
                                            session_id=req.session_id)

        if req.turn_summary == "(conversation start)":
            msg = req.alien_dialog
        else:
            msg = f'The player said: {req.turn_summary}'

        content = genai_types.Content(
            role="user", parts=[genai_types.Part(text=msg)]
        )

        raw = ""
        async for event in runner.run_async(user_id=PLAYER_ID,
                                            session_id=req.session_id,
                                            new_message=content):
            if event.is_final_response() and event.content and event.content.parts:
                raw = event.content.parts[0].text or ""
                if raw:
                    break

        if not raw:
            raise HTTPException(status_code=500, detail="No response from alien agent")

        reply = _unwrap_reply(raw)
        return {"reply": reply}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)