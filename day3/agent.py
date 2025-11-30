import json
import os
import time
from termcolor import colored
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# --- 1. Define Tools ---
def get_weather(location: str):
    """Mock weather function"""
    if "tokyo" in location.lower():
        return json.dumps({"temp": 10, "unit": "C"})
    elif "sf" in location.lower() or "san francisco" in location.lower():
        return json.dumps({"temp": 72, "unit": "F"})
    return json.dumps({"temp": 22, "unit": "C"})

def calculate(expression: str):
    """Safe math calculator"""
    try:
        # DANGEROUS in prod, but fine for learning
        return str(eval(expression))
    except:
        return "Error calculating"

# Tool Definitions for OpenAI
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a math expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "The math expression to evaluate, e.g. '2 + 2'"}
                },
                "required": ["expression"]
            }
        }
    }
]

# --- 2. The Agent Class (The Core Loop) ---
class Agent:
    def __init__(self, name: str, client, system_prompt: str = ""):
        self.name = name
        self.client = client
        self.system_prompt = system_prompt
        self.messages = []
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})

    def manage_memory(self):
        """
        Simple Context Window Management.
        LLMs have a limit on how much text they can read (e.g., 8k tokens).
        If we don't trim the history, the agent will eventually crash.
        """
        MAX_MESSAGES = 10 
        
        if len(self.messages) > MAX_MESSAGES + 1: # +1 for System Prompt
            # Always keep the System Prompt (index 0)
            system_msg = self.messages[0]
            
            # Keep only the last N messages
            recent_msgs = self.messages[-MAX_MESSAGES:]
            
            # Reconstruct memory
            self.messages = [system_msg] + recent_msgs
            print(colored(f"  [System] Memory Full. Trimmed to last {MAX_MESSAGES} messages.", "light_grey"))

    def run(self, user_input: str):
        """
        The Main Agent Loop:
        1. Append user input
        2. Call LLM
        3. If LLM wants to call tool -> Execute Tool -> Append Result -> Loop back to 2
        4. If LLM returns text -> Print it -> Break loop
        """
        self.messages.append({"role": "user", "content": user_input})
        
        # Check memory before starting the turn
        self.manage_memory()
        
        # Safety valve to prevent infinite loops
        max_turns = 5
        turn_count = 0

        while turn_count < max_turns:
            turn_count += 1
            print(colored(f"\n[Loop {turn_count}] Calling LLM...", "cyan"))
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=self.messages,
                tools=tools,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            # Case 1: The LLM wants to call a tool
            if message.tool_calls:
                self.messages.append(message) # Add the "intent" to history
                
                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    
                    print(colored(f"  --> Agent decided to call: {func_name}({args})", "yellow"))
                    
                    # Execute the tool
                    result = ""
                    if func_name == "get_weather":
                        result = get_weather(args["location"])
                    elif func_name == "calculate":
                        result = calculate(args["expression"])
                    
                    print(colored(f"  <-- Tool Output: {result}", "green"))
                    
                    # Add result to history
                    self.messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": result
                    })
            
            # Case 2: The LLM has a final answer
            else:
                print(colored(f"\n{self.name}: {message.content}", "magenta"))
                self.messages.append(message)
                return message.content

# --- 3. Mock Client (For when API is out of credits) ---
class MockClient:
    def __init__(self):
        self.chat = self.MockChat()
    class MockChat:
        def __init__(self):
            self.completions = MockClient.MockCompletions()
    class MockCompletions:
        def create(self, model, messages, tools=None, tool_choice=None):
            last_msg = messages[-1]
            content = last_msg.get("content", "")
            
            # Simple heuristic to simulate intelligence
            if "weather" in str(content).lower() and "tool" not in str(messages[-1].get("role")):
                return MockResponse(tool_calls=[
                    MockToolCall("get_weather", '{"location": "Tokyo"}', "call_1")
                ])
            elif "calculate" in str(content).lower() or "math" in str(content).lower():
                 if "tool" not in str(messages[-1].get("role")):
                    return MockResponse(tool_calls=[
                        MockToolCall("calculate", '{"expression": "10 * 22"}', "call_2")
                    ])
            
            # If we just got tool output, summarize it
            if messages[-1].get("role") == "tool":
                return MockResponse(content="Based on the data, the weather is 10C and the calculation is 220.")
                
            return MockResponse(content="I can help with weather and math.")

# Helper classes for Mock
class MockResponse:
    def __init__(self, content=None, tool_calls=None):
        self.choices = [MockChoice(content, tool_calls)]
class MockChoice:
    def __init__(self, content, tool_calls):
        self.message = MockMessage(content, tool_calls)
class MockMessage:
    def __init__(self, content, tool_calls):
        self.content = content
        self.tool_calls = tool_calls
        self.role = "assistant"
    def to_dict(self): return {"role": "assistant", "content": self.content}

class MockToolCall:
    def __init__(self, name, args, id):
        self.id = id
        self.function = MockFunction(name, args)
class MockFunction:
    def __init__(self, name, args):
        self.name = name
        self.arguments = args

# --- 4. Main Entry Point ---
if __name__ == "__main__":
    # Force Mock Client for now since API quota is exceeded
    # api_key = os.getenv("OPENAI_API_KEY")
    api_key = None 
    
    if api_key:
        print("Using Real OpenAI API")
        client = OpenAI(api_key=api_key)
    else:
        print("Using MOCK Client (No API Key found)")
        client = MockClient()

    bot = Agent("Bot", client, system_prompt="You are a helpful assistant with access to weather and math tools.")
    
    # Interactive Loop
    while True:
        try:
            user_text = input(colored("\nYou: ", "white"))
            if user_text.lower() in ["exit", "quit"]:
                break
            
            bot.run(user_text)
            
        except KeyboardInterrupt:
            break
