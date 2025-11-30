import os
import json
import time
from enum import Enum
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from termcolor import colored
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# --- 1. Define the State & Agents ---
class AgentType(str, Enum):
    RESEARCHER = "researcher"
    WRITER = "writer"
    REVIEWER = "reviewer"

class Step(BaseModel):
    id: int = Field(description="Step number")
    description: str = Field(description="Detailed description of what needs to be done in this step")
    assigned_agent: AgentType = Field(description="Which agent should perform this step")
    dependencies: List[int] = Field(default=[], description="IDs of steps that must be completed before this one")

class Plan(BaseModel):
    steps: List[Step] = Field(description="The sequence of steps to achieve the goal")

# --- 2. The Worker Agents (Mocked for simplicity) ---
# In a real system, these would be full Agent classes from Day 3.

def run_researcher(task: str) -> str:
    print(colored(f"  [Researcher] Searching web for: '{task}'...", "yellow"))
    time.sleep(1) # Simulate work
    return f"Found 3 articles about '{task}'. Key facts: 1. AI is growing. 2. Python is popular. 3. Agents are the future."

def run_writer(task: str, context: str) -> str:
    print(colored(f"  [Writer] Drafting content based on research...", "blue"))
    time.sleep(1)
    return f"DRAFT: Based on the research ({context[:30]}...), here is a summary article about the topic."

def run_reviewer(task: str, context: str) -> str:
    print(colored(f"  [Reviewer] Checking for errors...", "magenta"))
    time.sleep(1)
    return f"APPROVED: The draft looks good. No hallucinations found."

# --- 3. The Orchestrator (The Manager) ---
class Orchestrator:
    def __init__(self, client):
        self.client = client
        self.context: Dict[int, str] = {} # Memory: Step ID -> Result

    def create_plan(self, goal: str) -> Plan:
        print(colored(f"\n[Orchestrator] Creating plan for: '{goal}'", "cyan"))
        
        try:
            completion = self.client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": "You are a project manager. Break down the user's goal into a logical plan of steps for your team (Researcher, Writer, Reviewer)."},
                    {"role": "user", "content": goal},
                ],
                response_format=Plan,
            )
            return completion.choices[0].message.parsed
        except Exception as e:
            print(colored(f"Planning Error: {e}", "red"))
            return Plan(steps=[])

    def execute_plan(self, plan: Plan):
        print(colored("\n[Orchestrator] Executing Plan...", "cyan"))
        
        for step in plan.steps:
            print(colored(f"\nStep {step.id}: {step.description} (Assigned to: {step.assigned_agent.value})", "white"))
            
            # Gather context from previous steps (simple concatenation for now)
            # In a real system, you'd be smarter about what context to pass.
            previous_context = "\n".join([f"Step {k}: {v}" for k, v in self.context.items()])
            
            result = ""
            if step.assigned_agent == AgentType.RESEARCHER:
                result = run_researcher(step.description)
            elif step.assigned_agent == AgentType.WRITER:
                result = run_writer(step.description, previous_context)
            elif step.assigned_agent == AgentType.REVIEWER:
                result = run_reviewer(step.description, previous_context)
            
            # Store result in memory
            self.context[step.id] = result
            print(colored(f"  -> Result: {result}", "green"))

            # --- Human in the Loop (Advanced) ---
            # For critical steps (like Review), ask the user for approval before proceeding.
            if step.assigned_agent == AgentType.REVIEWER:
                user_approval = input(colored("\n[System] Reviewer finished. Proceed to publish? (y/n): ", "red"))
                if user_approval.lower() != 'y':
                    print(colored("  -> Stopping execution based on user feedback.", "red"))
                    break

        print(colored("\n[Orchestrator] Mission Complete!", "cyan"))

# --- 4. Mock Client (For testing) ---
class MockOrchestratorClient:
    def __init__(self):
        self.beta = self.MockBeta()
    class MockBeta:
        def __init__(self):
            self.chat = MockOrchestratorClient.MockChat()
    class MockChat:
        def __init__(self):
            self.completions = MockOrchestratorClient.MockCompletions()
    class MockCompletions:
        def parse(self, model, messages, response_format):
            # Return a fixed plan for demonstration
            return MockResponse(Plan(steps=[
                Step(id=1, description="Research the latest trends in Multi-Agent Systems", assigned_agent=AgentType.RESEARCHER),
                Step(id=2, description="Write a blog post summarizing the research", assigned_agent=AgentType.WRITER, dependencies=[1]),
                Step(id=3, description="Review the blog post for accuracy", assigned_agent=AgentType.REVIEWER, dependencies=[2])
            ]))

class MockResponse:
    def __init__(self, parsed_obj):
        self.choices = [MockChoice(parsed_obj)]
class MockChoice:
    def __init__(self, parsed_obj):
        self.message = MockMessage(parsed_obj)
class MockMessage:
    def __init__(self, parsed_obj):
        self.parsed = parsed_obj

# --- 5. Main Entry Point ---
if __name__ == "__main__":
    # Force Mock for now
    api_key = None # os.getenv("OPENAI_API_KEY")
    
    if api_key:
        print("Using Real OpenAI API")
        client = OpenAI(api_key=api_key)
    else:
        print("Using MOCK Orchestrator Client")
        client = MockOrchestratorClient()

    manager = Orchestrator(client)
    
    user_goal = "Research the latest trends in Multi-Agent Systems and write a verified blog post about it."
    
    # 1. Plan
    plan = manager.create_plan(user_goal)
    
    # 2. Execute
    if plan.steps:
        manager.execute_plan(plan)
    else:
        print("Failed to generate plan.")
