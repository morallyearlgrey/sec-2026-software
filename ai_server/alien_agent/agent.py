from fastapi import APIRouter
from pydantic import BaseModel, Field
from google.adk.agents import Agent
from alien_generator import Alien

alien = Alien()

# Specify the agent input/output text data structures
class PlayerInput(BaseModel):
    #message
    current_points = alien.get_points()

class AlienOutput(BaseModel):
    alien_dialog = Field(
        description = "The AI response to send to dialogic"
    )
    
    turn_summary = Field(
        description = "A 1-sentence summary of the interaction"
    )
    
root_agent = Agent(
    name="alien_agent",
    model="gemini-2.0-flash",
    instruction=alien.get_prompt(),
    output_schema = AlienOutput
    tools=[]
)

# Store the conversation state
