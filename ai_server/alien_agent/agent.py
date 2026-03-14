from fastapi import APIRouter
from pydantic import BaseModel, Field
from google.adk.agents import Agent
from .alien_generator import Alien
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types 
import json

class PlayerInput(BaseModel):
    player_id: str
    alien_id: str
    message: str
    current_points: int

class AlienOutput(BaseModel):
    alien_dialogue: str = Field(description="The AI response")
    turn_summary: str = Field(description="1-sentence summary")

session_service = InMemorySessionService()
router = APIRouter(prefix="/alien", tags=["Alien API"])

# Use strings for keys since player_id and alien_id are strings
aliens: dict[str, Alien] = {}

def get_or_create_alien(alien_id: str) -> Alien:    
    if alien_id not in aliens:
        new_alien = Alien()
        # Note: Changed to gemini-2.0-flash (standard stable version)
        root_agent = Agent(
            name=f"alien_agent_{alien_id}",
            model="gemini-2.0-flash", 
            instruction=new_alien.get_prompt(),
            output_schema=AlienOutput,
            tools=[]
        )
        
        new_alien.set_session(Runner(
            app_name="alien_game", 
            agent=root_agent,
            session_service=session_service
        ))
        
        aliens[alien_id] = new_alien
        
    return aliens[alien_id]

@router.get("/chat")
async def get_chat(index: str): # Changed to str to match dictionary
    alien_instance = get_or_create_alien(index)
    current_turn = alien_instance.get_turn()
    
    if current_turn > 5:
        return {"dialogue": "[TURN LIMIT REACHED]", "status": "closed"}

    if current_turn == 0:
        return {
            "dialogue": alien_instance.get_greeting(),
            "alien": alien_instance.get_dict(),
            "status": "open"
        }
    
    return {"dialogue": "Hmm.. we've already talked before.", "status": "closed"}

@router.post("/chat")
async def chat_with_alien(payload: PlayerInput):
    alien_instance = get_or_create_alien(payload.alien_id)
    combined_id = f"{payload.player_id}_{payload.alien_id}"
    
    # ── SESSION HANDSHAKE ──────────────────────────────────────────
    # If the GET request didn't create the session, we do it here.
    try:
        await session_service.get_session(
            session_id=combined_id, 
            app_name="alien_game", 
            user_id=payload.player_id
        )
    except Exception:
        print(f"DEBUG: Session {combined_id} not found, creating now...")
        await session_service.create_session(
            session_id=combined_id,
            app_name="alien_game",
            user_id=payload.player_id
        )

    # ── AI EXECUTION ───────────────────────────────────────────────
    injected_prompt = f"Points: {payload.current_points}\nTurn: {alien_instance.get_turn()}\n\n{payload.message}"
    
    full_response_obj = None
    try:
        # We wrap the run in a list to force the generator to exhaust immediately
        events = list(alien_instance.adk_session.run(
            user_id=payload.player_id,
            session_id=combined_id,
            new_message=injected_prompt # ADK handles string-to-Content conversion
        ))
        
        for event in events:
            if hasattr(event, 'output') and event.output:
                full_response_obj = event.output
    except Exception as e:
        print(f"CRITICAL AI ERROR: {e}")
        return {"error": "AI failed to respond", "details": str(e)}

    if not full_response_obj:
        return {"error": "No structured response received."}

    # ── STATE UPDATE ───────────────────────────────────────────────
    alien_instance.add_summary(full_response_obj.turn_summary)
    alien_instance.increment_turn()

    return {
        "dialogue": full_response_obj.alien_dialogue,
        "alien": alien_instance.get_dict(),
        "status": "open" 
    }