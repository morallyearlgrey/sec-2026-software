"""
qa_agent/agent.py  (place this file at ai_server/qa_agent/agent.py)

Wraps the lightweight prechecks logic in a Google ADK Agent so it can be
loaded by server.py exactly like the alien_agent.
"""

import re
from google.adk.agents import Agent
from google.adk.tools import FunctionTool


# ── pure-python validation helpers ────────────────────────────────────────────

def _is_empty(text: str) -> bool:
    return text == ""


def _is_valid_len(text: str) -> bool:
    return 3 < len(text) < 600


def prechecks(input: str) -> dict:
    """
    Run basic validity checks on the player's reply.

    Args:
        input: The raw player reply string.

    Returns:
        A dict with keys:
            validity (bool)  – True if the reply passed all checks.
            reason   (str)   – Human-readable explanation.
    """
    text = input.strip()
    if _is_empty(text):
        return {"validity": False, "reason": "Response is empty."}
    if not _is_valid_len(text):
        return {
            "validity": False,
            "reason": (
                "Response must be between 4 and 599 characters "
                f"(yours is {len(text)})."
            ),
        }
    return {"validity": True, "reason": "Good to go."}


# ── ADK agent ──────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """
You are a Quality-Assurance agent for a text adventure game.

Your ONLY job is to validate a player's reply to an alien NPC.

Workflow:
1. Call the `prechecks` tool with the player's reply text.
2. Read the tool result.
3. Respond with ONLY a JSON object — no preamble, no markdown fences — in the
   exact shape:
   {"validity": <true|false>, "reason": "<short explanation>", "summary": "<one sentence neutral restatement of the player reply, or empty string if invalid>"}

Rules:
- If prechecks returns validity=false, echo its reason and set summary to "".
- If prechecks returns validity=true, set validity=true, reason="", and write
  a single neutral sentence summarising what the player said.
- Never add commentary outside the JSON object.
""".strip()

root_agent = Agent(
    name="qa_agent",
    model="gemini-2.5-flash",
    instruction=_SYSTEM_PROMPT,
    tools=[FunctionTool(func=prechecks)],
)