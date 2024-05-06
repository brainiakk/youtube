import asyncio
import os
from langchain.agents import AgentExecutor, AgentType 
from langchain import hub
from langchain_google_genai import GoogleGenerativeAI
from langchain_community.utilities  import SerpAPIWrapper, WikipediaAPIWrapper, DuckDuckGoSearchAPIWrapper
from langchain_community.tools import DuckDuckGoSearchResults
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
from langchain_core.prompts import PromptTemplate
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from typing import Optional, Type, Dict, List
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import initialize_agent, AgentExecutor, create_structured_chat_agent

load_dotenv()
# Initialize LLMs and tools
llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=os.getenv("GOOGLE_API_KEY"))
minion_llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=os.getenv("GOOGLE_API_KEY"))
memory = ConversationBufferWindowMemory(
            memory_key='chat_history',
            k=3,
            return_messages=True
        )

class DDGSearchInput(BaseModel):
    query: str = Field(description="The search query from the user")
    region: str = Field(description="The country or region from the user query example: wt-wt, us-en, uk-en, ru-ru, etc. The default is wt-wt.", default="wt-wt")
    source: str = Field(description="The search engine source to get better results for the user search query, also check in the user original search query and if none was specified, Defaults to 'text'. These are the only options allowed: 'news', 'text', 'answers', 'images', 'videos', 'maps' and 'suggestions' ", default="text")
    
class DuckDuckGoSearchTool(BaseTool):
    name="Duck Duck Go Search Tool"
    description="Useful to search the web more for better results. This is a search engine tool."
    args_schema: Type[BaseModel] = DDGSearchInput
    
    def _run(self, query: str, region: str ="wt-wt", source: str ="text", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        wrapper = DuckDuckGoSearchAPIWrapper(region=region, max_results=5)
        search = DuckDuckGoSearchResults(api_wrapper=wrapper, source=source)
        return search.run(query)
 
    async def _arun(self, query: str, region: str ="wt-wt", source: str ="text", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        wrapper = DuckDuckGoSearchAPIWrapper(region=region,  max_results=5)
        search = await DuckDuckGoSearchResults(api_wrapper=wrapper, source=source)
        return search.run(query)

minion_tools = [DuckDuckGoSearchTool()]
# Define the minion agent
class MinionAgent:
    def __init__(self):
        self.task_complete = False
        self.result = None
        self.memory = memory
        self.llm = llm

    async def run(self, main_objective: str, task: dict):
        # self.result = initialize_agent(tools, llm=self.llm, agent='structured-chat-zero-shot-react-description',
        # max_iterations=2, 
        # early_stopping_method='generate',
        # handle_parsing_errors=True,
        # memory=self.memory, verbose=True)
        prompt = hub.pull("hwchase17/structured-chat-agent")
        agent = create_structured_chat_agent(llm, minion_tools, prompt)
        self.result = AgentExecutor(
            agent=agent, tools=minion_tools, verbose=True, handle_parsing_errors=True
        )
        
        self.result.ainvoke(
            {
                "system": f"""
                Your Project manager Brainiakk is currently working on {main_objective}. You are a loyal minion to Brainiakk. He needs you to complete your assigned task. Make sure you evaluate the task and complete it. Make Brainiakk proud.
                """,
                "input": f"Task: {task}"
            })
        # print(s)
        return await self.result
    
class Objectives(BaseModel):
    objective: str = Field(..., description="Each step for the minions to complete")
    
class ObjectiveRefinerInput(BaseModel):
    """Refine the main objective into actionable steps by other minions"""
    main_objective: str = Field(title='main_objective', description="The main objective from the user question or request.")
    steps: List[Objectives]
    
    
class MasterMind(BaseTool):
    name="Master Mind"
    description="Useful to breakdown complex tasks into smaller tasks with objectives. input should be the concise and detailed step by step plan to complete a complex task the user gave you. IMPORTANT: Only use this tool after gathering necessary information "
    args_schema: Type[BaseModel] = ObjectiveRefinerInput
    minion = MinionAgent()
   
    async def _run(self, main_objective: str, steps: list, run_manager: Optional[CallbackManagerForToolRun] = None):
        # Assign tasks to minions asynchronously
        print("hello")
        tasks = [self.minion.run(main_objective, step.objective) for step in steps]
        print( step["objective"] for step in steps)
        results = asyncio.gather(*tasks)
        compiled_results = "\n Result: ".join(await results)
        print(compiled_results)
        return compiled_results

    async def _arun(self, main_objective: str, steps: list, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        return await self._run(main_objective, steps, run_manager)
    
    
# Define the mastermind agent
class MastermindAgent:
    def __init__(self):
        self.llm = llm
        self.tools = tools
        self.memory = memory
        prompt = hub.pull("hwchase17/structured-chat-agent")
        agent = create_structured_chat_agent(llm, tools, prompt)

        self.mastermind = AgentExecutor(
            agent=agent, tools=tools, verbose=True, handle_parsing_errors=True
        )
        

    async def delegate_tasks(self, objective):
        main_prompt= ("You are the mastermind responsible for breaking down complex tasks into smaller sub-tasks. FYI: Agents are also known as minions"
            'Your output should be a dict called: "subtasks": [array of sub-task]'
              "After breaking down the task into sub-tasks, assign each sub-task to the best suited minion to execute."
              "Get what the minions returned and list out each sub-task and their respective results. "
              "Assess if the objective has been fully achieved. If the previous sub-task results comprehensively address all aspects of the objective,"
              "include the phrase 'The task is complete: ' at the beginning of your response. If the objective is not yet fully achieved,"
              "break it down into the next sub-task and create a concise and detailed prompt for a minion to execute that task."
              "Validate and analyze the results from each minion and assign a status to each sub-task as you list it with the result."
              "Any incomplete sub-task should be assigned to another minion before providing a general status and conclusion of the task.")
        # prompt = PromptTemplate.from_template(main_prompt)
        # Break down the objective into subtasks
        mastermind = self.mastermind.invoke(
            {
                "system": main_prompt,
                "input": f"objective: {objective}"
            })

        return mastermind

tools = [DuckDuckGoSearchTool(), MasterMind()]

# Create mastermind and minions
mastermind = MastermindAgent()

# Example usage
objective = "Plan an AI project like JARVIS"
final_response, task_completion = asyncio.run(mastermind.delegate_tasks(objective))

print(f"Final response: {final_response}")
print(f"Task completion status: {task_completion}")
