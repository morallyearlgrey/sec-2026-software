from fastapi import APIRouter
from pydantic import BaseModel, Field
from google.adk.agents import Agent
from alien_generator import Alien

class PlayerInput(BaseModel):
    player_id: str
    alien_id: str
    message: str

class AlienOutput(BaseModel):
    alien_dialogue: str = Field(description="The AI response")
    turn_summary: str = Field(description="1-sentence summary")

router = APIRouter(prefix="/alien", tags=["Alien API"])

# The multi-user, multi-alien memory store
active_sessions = {}

def get_or_create_alien(player_id: str, alien_id: str) -> Alien:
    # 1. Check if the player exists, if not, create their profile
    if player_id not in active_sessions:
        active_sessions[player_id] = {}
    
    # 2. Check if this specific alien exists for this player
    if alien_id not in active_sessions[player_id]:
        new_alien = Alien()
        
        # Instantiate a unique Agent and Session for this specific interaction
        agent = Agent(
            name = f"alien_agent_{alien_id}",
            model = "gemini-2.0-flash",
            instruction = new_alien.get_prompt(),
            output_schema = AlienOutput,
            tools = []
        )
        
        new_alien.set_session(agent.start_session())
        active_sessions[player_id][alien_id] = new_alien
        
    return active_sessions[player_id][alien_id]

@router.post("/chat")
async def chat_with_alien(payload: PlayerInput):
    # Retrieve the specific Alien object from the nested dictionary
    alien_instance = get_or_create_alien(payload.player_id, payload.alien_id)
    current_turn = alien_instance.get_turn()

    if current_turn > 5:
        return {
            "dialogue": "[TURN LIMIT REACHED]",
            "status": "closed",
            "summaries": alien_instance.get_summaries()
        }

    injected_prompt = f"""
<game_state>
Current Alien Trust Points: {payload.current_points}
Turn: {current_turn} of 5
</game_state>

<player_dialogue>
{payload.message}
</player_dialogue>
"""

    response = alien_instance.adk_session.send_message(injected_prompt)

    alien_instance.add_summary(response.turn_summary)
    alien_instance.increment_turn()

    return {
        "dialogue": response.alien_dialogue,
        "alien": alien_instance.get_dict()
    }