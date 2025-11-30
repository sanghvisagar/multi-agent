# Day 7: Shared State (The Blackboard Pattern)

## Why this matters?
In simple systems, Agent A talks to Agent B directly.
In complex systems, this becomes a mess ($N^2$ connections).

The **Blackboard Pattern** solves this:
1.  **Central Memory**: A shared object (the Blackboard) holds the state of the world.
2.  **Stateless Agents**: Agents read from the Blackboard, do work, and write back to it.
3.  **Decoupling**: The Researcher doesn't need to know the Writer exists. It just puts notes on the board.

## The Code (`shared_state.py`)
We define a `Blackboard` class using Pydantic.
- It holds `research_notes`, `draft_content`, etc.
- Agents (`Researcher`, `Writer`) take the `Blackboard` as input and return it modified.

## How to Run
1.  Install dependencies:
    ```bash
    pip install -r day7/requirements.txt
    ```
2.  Run the script:
    ```bash
    python day7/shared_state.py
    ```

## Key Takeaway
This pattern is essential for **State Management** in distributed systems. It allows you to inspect the entire state of your AI application at any point in time (great for debugging!).
