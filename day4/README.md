# Day 4: Task Routing (The Router Pattern)

## Why this matters?
In a Multi-Agent system, you rarely have one "Super Agent" that does everything. Instead, you have specialized agents:
- A **Coder** who is good at Python.
- A **Researcher** who is good at searching the web.
- A **Reviewer** who checks for errors.

The **Router** is the traffic controller. It takes the user's request and decides *who* should handle it. This is a specific deliverable in your job description: *"Develop task router for agent activation"*.

## The Code (`router.py`)
We use **Structured Outputs** (from Day 2) to build a robust classifier.

1.  **`AgentType` Enum**: Defines the valid destinations.
2.  **`Route` Model**: The Pydantic model that the LLM *must* return. It includes:
    - `agent`: The selected agent.
    - `reasoning`: Why it chose that agent (crucial for debugging).
    - `confidence`: How sure it is.
3.  **Dispatcher**: A simple `if/else` block that calls the correct function based on the Router's decision.

## How to Run
1.  Install dependencies:
    ```bash
    pip install -r day4/requirements.txt
    ```
2.  Run the router:
    ```bash
    python day4/router.py
    ```

## What to Watch For
Notice how the system handles different types of queries.
- "Write code" -> **Coding Agent**
- "Is it raining?" -> **Weather Agent**
- "Tell me a joke" -> **General Agent**

This pattern allows you to scale. You can add 50 specialized agents, and as long as your Router is smart, the user experience remains simple.
