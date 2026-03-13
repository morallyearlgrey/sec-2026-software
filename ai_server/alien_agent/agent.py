from google.adk.agents import Agent
from alien_generator import AlienGenerator

alien = AlienGenerator()

root_agent = Agent(
    name="alien_agent",
    model="gemini-2.0-flash",
    instruction=f"{alien.get_prompt()}",
    tools=[]
)