import os
import json
import time
from termcolor import colored
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# --- 1. The Unreliable Coder (Simulates an LLM making mistakes) ---
class MockCoderClient:
    def __init__(self):
        self.attempt = 0
        self.chat = self.MockChat(self)

    class MockChat:
        def __init__(self, parent):
            self.parent = parent
            self.completions = MockCoderClient.MockCompletions(parent)

    class MockCompletions:
        def __init__(self, parent):
            self.parent = parent

        def create(self, model, messages):
            self.parent.attempt += 1
            print(colored(f"\n[LLM] Generating code (Attempt {self.parent.attempt})...", "cyan"))
            time.sleep(1)

            # First attempt: Generate buggy code
            if self.parent.attempt == 1:
                code = """
def calculate_average(numbers):
    total = sum(numbers)
    # Bug: Dividing by zero if list is empty, and returning string instead of float
    return "The average is: " + str(total / 0) 
"""
                return MockResponse(code)
            
            # Second attempt: Fix the ZeroDivisionError but still return string
            elif self.parent.attempt == 2:
                code = """
def calculate_average(numbers):
    if not numbers:
        return 0
    total = sum(numbers)
    # Bug: Still returning string, but we want a float for the test
    return "The average is: " + str(total / len(numbers))
"""
                return MockResponse(code)

            # Third attempt: Correct code
            else:
                code = """
def calculate_average(numbers):
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)
"""
                return MockResponse(code)

class MockResponse:
    def __init__(self, content):
        self.choices = [MockChoice(content)]
class MockChoice:
    def __init__(self, content):
        self.message = MockMessage(content)
class MockMessage:
    def __init__(self, content):
        self.content = content

# --- 2. The Executor (The "Compiler/Tester") ---
def execute_and_test(code_str: str):
    """
    Compiles the code and runs a test case.
    Returns (Success: bool, Output/Error: str)
    """
    print(colored("  [System] Executing code...", "yellow"))
    
    # --- Static Analysis (Linter) ---
    # Before running, check for obvious bad practices
    if "eval(" in code_str or "exec(" in code_str:
        return False, "SecurityError: Use of 'eval' or 'exec' is forbidden."
    
    if "print" in code_str and "return" not in code_str:
        return False, "LintError: Function prints but does not return a value."

    # Define a local scope to run the code in
    local_scope = {}
    
    try:
        # 1. Compile and Execute the function definition
        exec(code_str, {}, local_scope)
        
        # 2. Check if function exists
        if "calculate_average" not in local_scope:
            return False, "Error: Function 'calculate_average' not defined."
        
        # 3. Run Test Case
        func = local_scope["calculate_average"]
        test_data = [10, 20, 30]
        result = func(test_data)
        
        # 4. Validate Result
        if not isinstance(result, (int, float)):
            return False, f"TypeError: Expected float, got {type(result).__name__} ('{result}')"
        
        if result != 20.0:
            return False, f"LogicError: Expected 20.0, got {result}"
            
        return True, "Tests Passed!"

    except Exception as e:
        return False, f"{type(e).__name__}: {str(e)}"

# --- 3. The Self-Correction Loop ---
def run_coding_task(client, task_description: str):
    messages = [
        {"role": "system", "content": "You are a Python coding assistant. Write code that satisfies the user request."},
        {"role": "user", "content": task_description}
    ]
    
    max_retries = 5
    
    for i in range(max_retries):
        # 1. Ask LLM for code
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        code = response.choices[0].message.content
        
        print(colored(f"  -> Generated Code:\n{code.strip()}", "white"))
        
        # 2. Test the code
        success, feedback = execute_and_test(code)
        
        if success:
            print(colored(f"\n[Success] {feedback}", "green"))
            return code
        else:
            print(colored(f"\n[Failure] {feedback}", "red"))
            print(colored("  -> Feeding error back to LLM...", "magenta"))
            
            # 3. Feed error back to LLM
            messages.append({"role": "assistant", "content": code})
            messages.append({"role": "user", "content": f"The code failed with this error:\n{feedback}\nPlease fix it."})
            
    print(colored("\n[Fatal] Max retries reached. Could not fix code.", "red"))
    return None

# --- 4. Main Entry Point ---
if __name__ == "__main__":
    # Force Mock for demonstration
    client = MockCoderClient()
    
    task = "Write a function 'calculate_average(numbers)' that returns the average of a list of numbers."
    
    print(colored(f"Task: {task}", "blue"))
    final_code = run_coding_task(client, task)
