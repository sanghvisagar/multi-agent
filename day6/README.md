# Day 6: Error Recovery & Self-Correction

## Why this matters?
LLMs are probabilistic, not deterministic. They make mistakes. They hallucinate APIs, forget imports, or write buggy code.
A "Senior Engineer" doesn't just hope the LLM gets it right; they build systems that **expect failure and recover from it**.

## The Pattern: Self-Correction Loop
1.  **Generate**: Ask the LLM to produce an output (e.g., code, JSON).
2.  **Validate**: Run a deterministic check (Compiler, Linter, Unit Test, JSON Validator).
3.  **Feedback**: If validation fails, capture the error message.
4.  **Refine**: Send the error message *back* to the LLM and ask it to fix the mistake.

## The Code (`self_correction.py`)
This script simulates a "Coding Agent" that is trying to write a `calculate_average` function.
- **Attempt 1**: It writes code that divides by zero. -> **System catches `ZeroDivisionError`**.
- **Attempt 2**: It fixes the zero division but returns a String instead of a Float. -> **System catches `TypeError`**.
- **Attempt 3**: It writes the correct code. -> **System passes tests**.

## How to Run
1.  Install dependencies:
    ```bash
    pip install -r day6/requirements.txt
    ```
2.  Run the script:
    ```bash
    python day6/self_correction.py
    ```

## Key Takeaway
This loop turns a "flaky" 80% accurate model into a robust 99% accurate system. You are trading **latency** (more calls) for **reliability**.
