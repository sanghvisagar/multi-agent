# Day 5: Orchestration Patterns (The Manager)

## Why this matters?
The job description asks for *"Implement agent orchestrator with coordination"*.

In Day 4, we built a **Router** (1-to-1 dispatch).
In Day 5, we build an **Orchestrator** (1-to-Many coordination).

This is often called the **Plan-and-Execute** pattern.
1.  **Manager Agent**: Receives a high-level goal.
2.  **Planning**: Breaks the goal into a dependency graph (Steps).
3.  **Execution**: Assigns each step to a specialized worker.
4.  **Context Passing**: Passes the output of Step 1 as input to Step 2.

## The Code (`orchestrator.py`)
We define a `Plan` model using Pydantic.
The `Orchestrator` class:
1.  Uses the LLM to generate a `Plan` object (List of `Step`s).
2.  Iterates through the steps.
3.  Calls the appropriate worker (`Researcher`, `Writer`, `Reviewer`).
4.  Maintains a `context` dictionary (Shared Memory) so workers can see what happened before.

## How to Run
1.  Install dependencies:
    ```bash
    pip install -r day5/requirements.txt
    ```
2.  Run the orchestrator:
    ```bash
    python day5/orchestrator.py
    ```

## Key Takeaway
This pattern allows you to solve **complex, multi-step problems** that a single prompt could never handle. It is the basis for systems like AutoGPT or BabyAGI.
