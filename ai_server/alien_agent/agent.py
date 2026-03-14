from fastapi import APIRouter
from pydantic import BaseModel, Field
from google.adk.agents import Agent
from .alien_generator import Alien
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types 

class PlayerInput(BaseModel):
    player_id: str
    alien_id: str
    message: str
    current_points: int

class AlienOutput(BaseModel):
    alien_dialogue: str = Field(description="The AI response")
    turn_summary: str = Field(description="1-sentence summary")

# Initialize the global session service
session_service = InMemorySessionService()

router = APIRouter(prefix="/alien", tags=["Alien API"])
active_sessions = {}

def get_or_create_alien(player_id: str, alien_id: str):
    if player_id not in active_sessions:
        active_sessions[player_id] = {}
    
    if alien_id not in active_sessions[player_id]:
        new_alien = Alien()
        root_agent = Agent(
            name=f"alien_agent_{alien_id}",
            model="gemini-2.0-flash",
            instruction=new_alien.get_prompt(),
            output_schema=AlienOutput,
            tools=[]
        )
        
        # Initialize the Runner with the global session_service
        new_alien.set_session(Runner(
            app_name="alien_game", 
            agent=root_agent,
            session_service=session_service
        ))
        
        active_sessions[player_id][alien_id] = new_alien
        
    return active_sessions[player_id][alien_id]

@router.post("/chat")
async def chat_with_alien(payload: PlayerInput):
    alien_instance = get_or_create_alien(payload.player_id, payload.alien_id)
    current_turn = alien_instance.get_turn()
    combined_id = f"{payload.player_id}_{payload.alien_id}"

    if current_turn > 5:
        return {"dialogue": "[TURN LIMIT REACHED]", "status": "closed"}

    # --- FINAL SESSION INITIALIZATION FIX ---
    try:
        # These MUST be awaited!
        await session_service.get_session(session_id=combined_id)
    except Exception:
        print(f"DEBUG: Creating session {combined_id}...")
        await session_service.create_session(
            session_id=combined_id,
            app_name="alien_game",
            user_id=payload.player_id
        )
    # ----------------------------------------

    injected_prompt = f"""
<game_state>
Current Alien Trust Points: {payload.current_points}
Turn: {current_turn} of 5
</game_state>

<player_dialogue>
{payload.message}
</player_dialogue>
"""
    user_content = types.Content(
        role="user", 
        parts=[types.Part(text=injected_prompt)]
    )

    full_response_obj = None

    # Keep the regular 'for' loop for the runner's generator
    for event in alien_instance.adk_session.run(
        user_id=payload.player_id,
        session_id=combined_id,
        new_message=user_content 
    ):
        if hasattr(event, 'output') and event.output:
            full_response_obj = event.output
        elif isinstance(event, AlienOutput):
            full_response_obj = event

    if not full_response_obj:
        return {"error": "Failed to retrieve a structured response."}

    alien_instance.add_summary(full_response_obj.turn_summary)
    alien_instance.increment_turn()

    return {
        "dialogue": full_response_obj.alien_dialogue,
        "alien": alien_instance.get_dict() 
    }