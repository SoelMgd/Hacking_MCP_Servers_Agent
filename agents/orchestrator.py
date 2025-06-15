from smolagents import CodeAgent, Tool


from prompts.orchestrator import SYSTEM_PROMPT
from agents.auditor import auditor_agent

orchestrator_agent = CodeAgent(
    system_prompt=SYSTEM_PROMPT,
    tools=[],
    managed_agents=[auditor_agent],
    name="Orchestrator"
)

