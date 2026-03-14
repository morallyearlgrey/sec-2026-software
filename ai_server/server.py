import os
import sys
import json
import re
import importlib
import importlib.util
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.sessions import InMemorySessionService

load_dotenv()

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYER_ID = "mcdiggity"

# Directory layout expected:
#   ai_server/
#     server.py
#     alien_generator.py
#     alien_agent/
#       agent.py          ← alien personality agent
#     qa_agent/
#       agent.py          ← QA agent (wraps prechecks via FunctionTool)

_ALIEN_AGENT_DIR = os.path.join(AGENT_DIR, "alien_agent")
_QA_AGENT_DIR    = os.path.join(AGENT_DIR, "qa_agent")

for _p in [AGENT_DIR, _ALIEN_AGENT_DIR, _QA_AGENT_DIR]:
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

_qa_svc    = InMemorySessionService()
_alien_svc = InMemorySessionService()

app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    allow_origins=["*"],
    web=True,
)


# ── agent loaders ──────────────────────────────────────────────────────────────

def _load_module(mod_name: str, file_path: str, package: str):
    """Load a Python module from an absolute file path, cached in sys.modules."""
    if mod_name not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            mod_name, file_path, submodule_search_locations=[]
        )
        mod             = importlib.util.module_from_spec(spec)
        mod.__package__ = package
        sys.modules[mod_name] = mod
        spec.loader.exec_module(mod)
    return sys.modules[mod_name]


def _load_qa_agent():
    mod = _load_module(
        "qa_agent.agent",
        os.path.join(_QA_AGENT_DIR, "agent.py"),
        "qa_agent",
    )
    return mod.root_agent


def _load_alien_agent():
    mod = _load_module(
        "alien_agent.agent",
        os.path.join(_ALIEN_AGENT_DIR, "agent.py"),
        "alien_agent",
    )
    return mod.root_agent


# ── helpers ────────────────────────────────────────────────────────────────────

def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    return text.strip()


def _parse_qa_response(raw: str) -> dict:
    """Extract {validity, reason, summary} from whatever the QA agent returns."""
    cleaned = _strip_fences(raw)
    # Try every JSON object in the response, back-to-front
    for blob in reversed(list(re.finditer(r'\{[^{}]+\}', cleaned, re.DOTALL))):
        try:
            obj = json.loads(blob.group())
            if "validity" in obj:
                v = obj["validity"]
                if isinstance(v, str):
                    obj["validity"] = v.strip().lower() == "true"
                obj.setdefault("reason",  "")
                obj.setdefault("summary", "")
                return obj
        except Exception:
            continue
    try:
        obj = json.loads(cleaned)
        if isinstance(obj, dict) and "validity" in obj:
            return obj
    except Exception:
        pass
    return {"validity": False, "reason": raw[:300], "summary": ""}


def _unwrap_alien_reply(raw: str) -> str:
    raw = raw.strip()
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict):
            for key in ("alien_dialog", "reply", "response", "message", "text"):
                if key in obj and isinstance(obj[key], str):
                    return obj[key]
            for v in obj.values():
                if isinstance(v, str) and v:
                    return v
    except Exception:
        pass
    return raw


# ── request models ─────────────────────────────────────────────────────────────

class QARequest(BaseModel):
    session_id: str
    question:   str
    answer:     str


class AlienRequest(BaseModel):
    session_id:   str
    alien_dialog: str
    turn_summary: str
    alien_prompt: str = ""


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
    Generate a fresh random alien character.
    Returns all fields needed by the Godot client, including a system prompt.
    """
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
            f"you are an {mbti}. You work as a {situation[0]} at a market booth "
            f"selling {situation[1]}. You enjoy {likes[0]}, {likes[1]}, and {likes[2]}. "
            f"You dislike {dislikes[0]}, {dislikes[1]}, and {dislikes[2]}. "
            f"You have at most 5 exchanges before you want to wrap up the conversation. "
            f"Your opening greeting is: \"{greeting}\". "
            f"Someone has approached your booth and may try to invite you somewhere. "
            f"Respond only with natural conversational dialogue as your character. "
            f"Never output JSON. Never break character."
        )

        return {
            "name":         name,
            "mood":         mood,
            "mbti":         mbti,
            "situation":    situation,
            "greeting":     greeting,
            "likes":        likes,
            "dislikes":     dislikes,
            "liked_words":  liked_words,
            "banned_words": banned_words,
            "prompt":       prompt,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run-qa")
async def run_qa(req: QARequest):
    """
    Validate a player reply via the QA agent.
    Returns {validity: bool, reason: str, summary: str}.
    """
    from google.adk.runners import Runner
    from google.genai import types as genai_types

    try:
        agent  = _load_qa_agent()
        runner = Runner(agent=agent, app_name="qa_agent", session_service=_qa_svc)

        existing = await _qa_svc.get_session(
            app_name="qa_agent", user_id=PLAYER_ID, session_id=req.session_id
        )
        if existing is None:
            await _qa_svc.create_session(
                app_name="qa_agent", user_id=PLAYER_ID, session_id=req.session_id
            )

        msg = (
            f"Alien said: {req.question}\n"
            f"Player replied: {req.answer}\n\n"
            f"Validate the player's reply. Call the prechecks tool with: {req.answer}"
        )
        content = genai_types.Content(
            role="user", parts=[genai_types.Part(text=msg)]
        )

        raw = ""
        async for event in runner.run_async(
            user_id=PLAYER_ID, session_id=req.session_id, new_message=content
        ):
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
    """
    Send a player turn to the alien agent and get its next line.
    Returns {reply: str}.
    alien_prompt must be provided — it encodes this alien's unique personality.
    """
    from google.adk.runners import Runner
    from google.adk.agents import Agent
    from google.genai import types as genai_types

    try:
        if not req.alien_prompt:
            raise HTTPException(status_code=400, detail="alien_prompt is required")

        # Build agent fresh each call with this alien's personality.
        # The session stored in _alien_svc preserves conversation history.
        agent = Agent(
            name="alien_agent",
            model="gemini-2.5-flash",
            instruction=req.alien_prompt,
            tools=[],
        )

        runner = Runner(
            agent=agent, app_name="alien_agent", session_service=_alien_svc
        )

        existing = await _alien_svc.get_session(
            app_name="alien_agent", user_id=PLAYER_ID, session_id=req.session_id
        )
        if existing is None:
            await _alien_svc.create_session(
                app_name="alien_agent", user_id=PLAYER_ID, session_id=req.session_id
            )

        if req.turn_summary == "(conversation start)":
            msg = "Begin the conversation with your opening greeting."
        else:
            msg = f"The player responded: {req.turn_summary}"

        content = genai_types.Content(
            role="user", parts=[genai_types.Part(text=msg)]
        )

        raw = ""
        async for event in runner.run_async(
            user_id=PLAYER_ID, session_id=req.session_id, new_message=content
        ):
            if event.is_final_response() and event.content and event.content.parts:
                raw = event.content.parts[0].text or ""
                if raw:
                    break

        if not raw:
            raise HTTPException(status_code=500, detail="No response from alien agent")

        return {"reply": _unwrap_alien_reply(raw)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)