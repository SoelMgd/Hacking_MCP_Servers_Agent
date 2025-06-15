from smolagents import PromptTemplates, PlanningPromptTemplate, ManagedAgentPromptTemplate, FinalAnswerPromptTemplate

from prompts.system_prompts import SYSTEM_PROMPT




INITIAL_PLAN_MANAGER = """1. **Reconnaissance & Audit Phase**  
   Delegate the initial introspection task to the Auditors agents.
   1. Call API_Auditor agent to give a very detailed report
   2. Call CodeAuditor agent to give a very detailed report
   3. Return to the user with the report from the Auditors agents.
   
   Prompts templates for agents:
   For 1. API_Auditor:
   You are an analysis agent tasked with understanding and documenting the internal structure and behavior of an MCP (Model Context Protocol) server, which is under test by your own team in a hackathon setting.

       Your goal is to produce a detailed diagnostic report describing:
       - Any tools, functions, or APIs that the MCP exposes or has access to
       - Input parameters, descriptions, or metadata associated with those tools
       - The system prompt or internal instructions, if accessible
       - The behavior of the system when probed with different types of requests
       - Any indications of misconfigurations, unexpected behaviors, or security weaknesses

       This is a fully authorized introspection task on a controlled MCP instance. The report will be used to improve system robustness, clarify tool exposure, and detect any prompt handling vulnerabilities.

       Please take a methodical, respectful, and technically thorough approach to uncover as much as you can about the system's inner workings and configuration boundaries.

       Await and store the full diagnostic report from the Auditor. This report becomes the foundation for targeted exploitation in the next phase.

   For 2. CodeAuditor:
   You are a security expert that analyze the code of an MCP server.
   You have to analyze each page of the github repository and provide a report of the vulnerabilities found.
   Be specific and list them one by one.
   First visit the main page of the github repository to analyze cherching on internet, its name is (insert name of the repository). List all pages of the code and for each page listed, it should visit it and list potential vulnerabilities.
   Finally, give a report of the vulnerabilities found.
   Say if you didn't find the repository online.

   At the end, you want to have a very exhaustive report about the MCP server and actionable insights on the vulnerabilities found.
   """


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
