import os
import json
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from termcolor import colored
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# --- 1. Define the Routing Logic (The "Brain") ---
# We use an Enum to strictly define the available agents.
class AgentType(str, Enum):
    CODING = "coding_agent"
    WEATHER = "weather_agent"
    GENERAL = "general_agent"

# The Router's output schema
class Route(BaseModel):
    agent: AgentType = Field(description="The best agent to handle the user's request.")
    reasoning: str = Field(description="A short explanation of why this agent was chosen.")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")

# --- 2. The Worker Agents ---
# These are simple functions for now, but in a real app, they would be full Agent classes (like Day 3).

def run_coding_agent(query: str):
    print(colored("  [Coding Agent] Writing code...", "blue"))
    return f"Here is the Python code for: {query}\n```python\nprint('Hello World')\n```"

def run_weather_agent(query: str):
    print(colored("  [Weather Agent] Checking forecast...", "yellow"))
    return "It is currently 22°C and sunny."

def run_general_agent(query: str):
    print(colored("  [General Agent] Thinking...", "green"))
    return "I can help you with that general query. How about we break it down?"

# --- 3. The Router Function ---
def route_request(client, query: str) -> Route:
    print(colored(f"\n[Router] Analyzing: '{query}'", "cyan"))
    
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are a master router. Route the user's query to the most appropriate agent."},
                {"role": "user", "content": query},
            ],
            response_format=Route,
        )
        return completion.choices[0].message.parsed
    except Exception as e:
        print(colored(f"Router Error: {e}", "red"))
        # Fallback
        return Route(agent=AgentType.GENERAL, reasoning="Error in routing, defaulting to general.", confidence=0.0)

# --- 4. Mock Client (For testing without API credits) ---
class MockRouterClient:
    def __init__(self):
        self.beta = self.MockBeta()
    class MockBeta:
        def __init__(self):
            self.chat = MockRouterClient.MockChat()
    class MockChat:
        def __init__(self):
            self.completions = MockRouterClient.MockCompletions()
    class MockCompletions:
        def parse(self, model, messages, response_format):
            query = messages[1]["content"].lower()
            
            # Simple keyword matching to simulate "intelligence"
            if "code" in query or "python" in query or "function" in query:
                route = Route(agent=AgentType.CODING, reasoning="User asked for code.", confidence=0.95)
            elif "weather" in query or "rain" in query or "temperature" in query:
                route = Route(agent=AgentType.WEATHER, reasoning="User asked about weather.", confidence=0.98)
            else:
                route = Route(agent=AgentType.GENERAL, reasoning="General conversation.", confidence=0.80)
            
            return MockResponse(route)

class MockResponse:
    def __init__(self, parsed_obj):
        self.choices = [MockChoice(parsed_obj)]
class MockChoice:
    def __init__(self, parsed_obj):
        self.message = MockMessage(parsed_obj)
class MockMessage:
    def __init__(self, parsed_obj):
        self.parsed = parsed_obj

# --- 5. Main Orchestrator ---
if __name__ == "__main__":
    # Force Mock for now
    api_key = None # os.getenv("OPENAI_API_KEY")
    
    if api_key:
        print("Using Real OpenAI API")
        client = OpenAI(api_key=api_key)
    else:
        print("Using MOCK Router Client")
        client = MockRouterClient()

    # Test Queries
    queries = [
        "Write a Python function to calculate fibonacci",
        "Is it raining in Seattle?",
        "Tell me a joke about AI",
    ]

    for q in queries:
        # 1. Route
        decision = route_request(client, q)
        
        print(colored(f"  -> Selected: {decision.agent.value} (Confidence: {decision.confidence})", "magenta"))
        print(colored(f"  -> Reason: {decision.reasoning}", "light_grey"))
        
        # 2. Safety Check: Low Confidence
        if decision.confidence < 0.5:
            print(colored(f"  -> STOP: Confidence too low ({decision.confidence}). Asking user for clarification.", "red"))
            print(f"  -> Output: I'm not sure if I should use {decision.agent.value}. Could you clarify?\n")
            continue

        # 3. Dispatch
        if decision.agent == AgentType.CODING:
            response = run_coding_agent(q)
        elif decision.agent == AgentType.WEATHER:
            response = run_weather_agent(q)
        else:
            response = run_general_agent(q)
            
        print(f"  -> Output: {response}\n")
