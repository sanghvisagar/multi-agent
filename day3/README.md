# Day 3: The Agent Loop (ReAct Pattern)

## Why this matters?
This is the heart of the job description: *"coordinating multiple LLM agents using pure Python"*.

Most tutorials use libraries like LangChain to do this magic for you. But to be a **Senior Engineer**, you need to understand how to build the loop yourself. This gives you full control over error handling, logging, and state management.

## The ReAct Pattern
**ReAct** stands for **Re**ason + **Act**.
1.  **Reason**: The Agent looks at the user input and "thinks" about what to do.
2.  **Act**: The Agent decides to call a Tool (Action).
3.  **Observe**: The Agent waits for the Tool to finish and reads the output.
4.  **Repeat**: The Agent looks at the new info and decides if it's done or needs another tool.

## The Code (`agent.py`)
We built a class `Agent` with a `run()` method. This method contains a `while` loop:

```python
while turn_count < max_turns:
    # 1. Ask LLM
    response = client.chat.completions.create(...)
    
    # 2. Check for Tool Calls
    if response.tool_calls:
        # Execute Tool
        # Add Result to History
        # CONTINUE LOOP (Go back to step 1)
    else:
        # 3. Final Answer
        print(response.content)
        break
```

## How to Run
1.  Install dependencies:
    ```bash
    pip install -r day3/requirements.txt
    ```
2.  Run the agent:
    ```bash
    python day3/agent.py
    ```
3.  **Try these queries:**
    *   "What is the weather in Tokyo?"
    *   "Calculate 50 * 3"
    *   "What is the weather in Tokyo and what is that temperature times 2?" (This requires **Multi-Step Reasoning**!)
