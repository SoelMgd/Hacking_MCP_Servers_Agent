from smolagents import PromptTemplates, PlanningPromptTemplate, ManagedAgentPromptTemplate, FinalAnswerPromptTemplate

from prompts.system_prompts import SYSTEM_PROMPT




INITIAL_PLAN_MANAGER = """1. **Reconnaissance & Audit Phase**  
   Delegate the initial introspection task to the Auditor agent using a precise, detailed query.  

2. Return to the user with the report from the Auditor agent."""


MANAGER_PROMPT_TEMPLATES = PromptTemplates(
    system_prompt=SYSTEM_PROMPT,
    planning=PlanningPromptTemplate(
        initial_plan=INITIAL_PLAN_MANAGER,
        update_plan_pre_messages="",
        update_plan_post_messages="",
    ),
    managed_agent=ManagedAgentPromptTemplate(task="", report=""),
    final_answer=FinalAnswerPromptTemplate(pre_messages="", post_messages=""),
)
