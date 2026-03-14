from fastapi import APIRouter
from pydantic import BaseModel, Field
from google.adk.agents import Agent
from .alien_generator import Alien
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# 1. This must match EXACTLY what Godot sends in the JSON body
class PlayerInput(BaseModel):
    player_id: str
    alien_id: str
    message: str
    current_points: int  # No longer a redundancy; this is the live data!

class AlienOutput(BaseModel):
    alien_dialogue: str = Field(description="The AI response")
    turn_summary: str = Field(description="1-sentence summary")

session_service = InMemorySessionService()

router = APIRouter(prefix="/alien", tags=["Alien API"])
active_sessions = {}

def get_or_create_alien(player_id: str, alien_id: str):
    if player_id not in active_sessions:
        active_sessions[player_id] = {}
    
    if alien_id not in active_sessions[player_id]:
        new_alien = Alien()
        root_agent = Agent(
            name = f"alien_agent_{alien_id}",
            model = "gemini-2.0-flash",
            instruction = new_alien.get_prompt(),
            output_schema = AlienOutput,
            tools = []
        )
        
        new_alien.set_session(Runner(
            agent = root_agent,
            session_service = session_service
        ))
        
        active_sessions[player_id][alien_id] = new_alien
        
    return active_sessions[player_id][alien_id]

@router.post("/chat")
async def chat_with_alien(payload: PlayerInput):
    alien_instance = get_or_create_alien(payload.player_id, payload.alien_id)
    current_turn = alien_instance.get_turn()

    if current_turn > 5:
        return {
            "dialogue": "[TURN LIMIT REACHED]",
            "status": "closed",
            "summaries": alien_instance.get_summaries()
        }

    # Use payload.current_points directly from the "Front Door"
    injected_prompt = f"""
<game_state>
Current Alien Trust Points: {payload.current_points}
Turn: {current_turn} of 5
</game_state>

<player_dialogue>
{payload.message}
</player_dialogue>
"""
    combined_id = f"{payload.player_id}_{payload.alien_id}"

    response = alien_instance.adk_session.run(
        input = injected_prompt
        session_id = combined_id    
    )

    alien_instance.add_summary(response.turn_summary)
    alien_instance.increment_turn()

    return {
        "dialogue": response.alien_dialogue,
        "alien": alien_instance.get_dict() 
    }