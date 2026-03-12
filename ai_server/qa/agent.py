from google.adk.agents import Agent

root_agent = Agent(
    name="qa_agent",
    model="gemini-2.0-flash",
    instruction="",
    tools=[]
)