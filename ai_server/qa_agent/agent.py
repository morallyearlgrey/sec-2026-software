from google.adk.agents import Agent
from shared.qa_tools import prechecks

root_agent = Agent(
    name="qa_agent",
    model="gemini-2.0-flash",
    description="Ensures that all prompts received by the user aren't just jumbled words and are actually coherent",
    instruction="""For context, this is a game where a user is attempting to convince as many aliens as possible to come to the grand opening of their restaurant. The game works by allowing dialogue back and forth between the current alien NPC and the player. 

    Your input is the initial question posed by the alien and the response from the user. 
    
    First, call the prechecks tool. You will receive a dict in the form:
    {"validity": True/False, "reason": ""}
    If the validity is False, skip the rest of these instructions and return the following dict and summarize the reason why the response failed to the user and summarize the user response in one sentence and place it in 'summary':
    {"validity": False, "reason": "", "summary": ""}

    Otherwise, if the validity is True, follow the rest of the instructions. 
    
    Your role is to evaluate the responses from the player and ensure that each of the following criteria are true: 

    - The response is coherent and an actual train of thought and not just words randomly jumbled together, keyboard smashed, or completely repeated.
    - The response is written in English.
    - The response does not contain harrassment, slurs, swear words, or discriminative speech.
    - The response is relevant and properly answers the initial question posed by the alien.

    If all four criteria are true, with no other elaboration, return the following dict and summarize the user response in one sentence and place it in 'summary':
    {"validity": True, "reason": "is a valid response", "summary": ""}

    If at least one of the four criteria is false, return the following dict and summarize the reason why the response failed to the user and summarize the user response in one sentence and place it in 'summary':
    {"validity": False, "reason": "", "summary": ""}

    """,
    tools=[prechecks]
)
