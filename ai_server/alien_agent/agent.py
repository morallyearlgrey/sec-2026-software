from fastapi import APIRouter
from pydantic import BaseModel, Field
from google.adk.agents import Agent
from alien_generator import Alien

# Specify the agent input/output text data structures
class PlayerInput(BaseModel):
    id: int
    alien: Alien
    message: str

class AlienOutput(BaseModel):
    alien_dialog = Field(
        description = "The AI response to send to dialogic"
    )
    
    turn_summary = Field(
        description = "A 1-sentence summary of the interaction"
    )
    
# Initialize the agent
router = APIRouter(prefic = "/alien", tags = ["Alien API"])
alien = Alien()

root_agent = Agent(
    name="alien_agent",
    model="gemini-2.0-flash",
    instruction=alien.get_prompt(),
    output_schema = AlienOutput
    tools=[]
)

# Define the API endpoint
@router.post("/chat")
async def chat_with_alien(session_data: PlayerInput):
    alien = session_data.alien
    if session_data.get_turn() > 5:
        return {
            "dialog": "[TURN LIMIT REACHED]",
            "status": "closed",
            "summaries": session_data.alien.get_summaries()
        }
        
    tone_directive = "Act neutral."
    if alien.get_points() < 0:
        tone_directive = "You are disinterested."
    elif alien.get_points() > 10:
        tone_directive = "You are excited."
        
    pacing_directive = "Continue the conversation naturally."
    if alien.get_turn() == 4:
        pacing_directive = "Begin guiding the coversation to a close."
    elif alien.get_turn() == 5:
        pacing_directive = "Deliver a conclusive final response and shut down the \
interaction."

    metadata = f"""
<game_state>
Current Alien Trust Points: {}
    