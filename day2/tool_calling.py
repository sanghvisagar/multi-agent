import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# --- 1. Define the "Tool" (The Function) ---
# This is a real Python function that our Agent will be able to "call".
def get_current_weather(location: str, unit: str = "celsius"):
    """Get the current weather in a given location."""
    print(f"--> TOOL CALLED: get_current_weather('{location}', '{unit}')")
    
    # In a real app, you would call a weather API here.
    # We'll return mock data.
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": "fahrenheit"})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

# --- 2. Define the Tool Schema ---
# We need to tell OpenAI *how* to use this function.
# This is the "Function Definition".
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    }
]

# --- 3. The Execution Logic ---
def run_conversation():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found.")
        return

    client = OpenAI(api_key=api_key)
    
    # User asks a question that requires a tool
    user_query = "What's the weather like in San Francisco and Tokyo?"
    messages = [{"role": "user", "content": user_query}]

    print(f"User: {user_query}")

    # First Call: Send query + tools to LLM
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # Let the model decide whether to call a tool
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Check if the model wanted to call a tool
    if tool_calls:
        print(f"\nModel wants to call {len(tool_calls)} tools:")
        
        # Extend conversation with the assistant's reply (which contains the tool calls)
        messages.append(response_message)

        # --- 4. Execute the Tools ---
        # We must execute the function and give the result back to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            if function_name == "get_current_weather":
                function_response = get_current_weather(
                    location=function_args.get("location"),
                    unit=function_args.get("unit"),
                )
                
                # Add the tool output to the conversation history
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )

        # --- 5. Second Call: Get Final Answer ---
        # Now that the model has the tool outputs, ask it to formulate the final answer
        print("\nSending tool outputs back to model...")
        second_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        
        print("\nFinal Answer:")
        print(second_response.choices[0].message.content)

if __name__ == "__main__":
    run_conversation()
