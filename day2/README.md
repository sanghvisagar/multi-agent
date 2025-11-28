# Day 2: LLM APIs & Structured Outputs

## Why this matters?
In Day 1, we learned how to validate data *if* we have it. In Day 2, we learn how to **force** the LLM to give us that valid data in the first place.

For a Multi-Agent system, agents need to talk to each other. They can't just send paragraphs of text; they need to send structured data (JSON) so the next agent knows exactly what to do (e.g., `{"action": "search", "query": "python docs"}`).

## Key Concepts

### 1. Structured Outputs (OpenAI)
Modern LLM APIs (like OpenAI's `gpt-4o`) allow you to pass a JSON Schema (or a Pydantic model) directly to the API. The model is then **guaranteed** to return JSON that matches that schema. This eliminates 99% of parsing errors.

### 2. The `response_format` Parameter
In the OpenAI SDK, we use `client.beta.chat.completions.parse` and pass our Pydantic model to `response_format`. The SDK handles the conversion from Pydantic to JSON Schema for us.

## The Exercise: Unstructured Text -> Structured Event
We will build a script that takes a messy email/chat message and extracts a clean `CalendarEvent` object.

### Setup
1.  **Get an OpenAI API Key**: You will need an API key from [platform.openai.com](https://platform.openai.com/).
2.  **Create a `.env` file**:
    Create a file named `.env` in the `day2` folder (or root) and add your key:
    ```
    OPENAI_API_KEY=sk-proj-....
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r day2/requirements.txt
    ```

### Run the script
```bash
python day2/structured_extractor.py
```

### Code Walkthrough
Open `structured_extractor.py`:
- **`CalendarEvent`**: The Pydantic model defining what we want.
- **`Field(description=...)`**: These descriptions are sent to the LLM! They act as "mini-prompts" telling the LLM how to fill that specific field.
- **`client.beta.chat.completions.parse`**: The magic method that enforces the structure.
