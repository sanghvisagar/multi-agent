import json
import time

# --- Mocking the OpenAI Client ---
# Since we don't have a working API key, we will simulate what the LLM *would* do.
class MockOpenAIClient:
    def __init__(self):
        self.chat = self.MockChat()

    class MockChat:
        def __init__(self):
            self.completions = self.MockCompletions()

        class MockCompletions:
            def create(self, model, messages, tools=None, tool_choice=None):
                last_message = messages[-1]
                
                # 1. Simulate First Call (LLM decides to call tools)
                if tools and "weather" in last_message["content"].lower():
                    print("\n[MOCK LLM] Thinking... 'I need to check the weather for San Francisco and Tokyo'")
                    time.sleep(1)
                    return MockResponse(
                        tool_calls=[
                            MockToolCall("get_current_weather", '{"location": "San Francisco, CA", "unit": "fahrenheit"}', "call_1"),
                            MockToolCall("get_current_weather", '{"location": "Tokyo, Japan", "unit": "celsius"}', "call_2")
                        ]
                    )
                
                # 2. Simulate Second Call (LLM summarizes results)
                else:
                    print("\n[MOCK LLM] Thinking... 'I have the data, now I will summarize it.'")
                    time.sleep(1)
                    return MockResponse(
                        content="The current weather in San Francisco is 72°F, and in Tokyo it is 10°C."
                    )

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

class MockToolCall:
    def __init__(self, name, arguments, id):
        self.id = id
        self.function = MockFunction(name, arguments)

class MockFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

# --- Real Tool Logic (Same as before) ---
def get_current_weather(location: str, unit: str = "celsius"):
    """Get the current weather in a given location."""
    print(f"--> TOOL CALLED: get_current_weather('{location}', '{unit}')")
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": "fahrenheit"})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

# --- Main Execution (Modified to use Mock) ---
def run_conversation():
    print("--- RUNNING IN MOCK MODE (No API Key Required) ---")
    client = MockOpenAIClient()
    
    user_query = "What's the weather like in San Francisco and Tokyo?"
    messages = [{"role": "user", "content": user_query}]

    print(f"User: {user_query}")

    # First Call
    # We MUST pass a non-empty list of tools, otherwise the mock logic (line 19) 
    # won't trigger the "I need to call tools" branch.
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=[{"type": "function"}], # Dummy tool to trigger the mock logic
        tool_choice="auto",
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        print(f"\nModel wants to call {len(tool_calls)} tools:")
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            if function_name == "get_current_weather":
                function_response = get_current_weather(
                    location=function_args.get("location"),
                    unit=function_args.get("unit"),
                )
                
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )

        # Second Call
        print("\nSending tool outputs back to model...")
        second_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        
        print("\nFinal Answer:")
        print(second_response.choices[0].message.content)

if __name__ == "__main__":
    run_conversation()
