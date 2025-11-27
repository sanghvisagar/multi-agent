# Day 1: Modern Python Fundamentals for AI Agents

## Why this matters?
1. **AsyncIO**: LLMs are slow. If you ask an agent to do 5 things, you don't want to wait for them one by one (sequential). You want to fire them all off at once (concurrent). `asyncio` is how Python handles this.
2. **Pydantic**: LLMs output messy text. To build reliable systems, we need to force that text into structured objects. Pydantic is the industry standard for this validation.

## Key Concepts

### 1. AsyncIO (Concurrency)
- **`async def`**: Defines a function that can be paused (a coroutine).
- **`await`**: The keyword that says "pause here and let other things run while I wait for this slow thing (like a network request) to finish".
- **`asyncio.gather`**: The magic function that runs multiple async functions at the same time.

### 2. Pydantic (Validation)
- **`BaseModel`**: The class you inherit from to define your data schema.
- **Type Hints**: You use standard Python types (`str`, `int`, `List`) to define fields.
- **Automatic Validation**: If you try to put a string into an `int` field, Pydantic throws an error. This is crucial for catching LLM hallucinations.

## The Exercise: Async Web Scraper
We will build a script that:
1. Defines a strict schema for a webpage using **Pydantic**.
2. Fetches multiple URLs at the same time using **AsyncIO**.
3. Validates the incoming data against our schema.

### How to run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the script:
   ```bash
   python async_scraper.py
   ```

### Code Walkthrough
Open `async_scraper.py` to see the implementation. 
- Notice how `fetch_page` is defined with `async def`.
- Notice `ScrapedPage` inheriting from `BaseModel`.
- Notice `await asyncio.gather(*tasks)` which triggers the parallel execution.
