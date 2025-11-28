import os
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# --- 1. Define the Structure (The Schema) ---
# We want to extract specific information from unstructured text.
# Pydantic defines the "shape" we expect the LLM to fill.

class CalendarEvent(BaseModel):
    event_name: str = Field(description="The name of the event or meeting")
    date: str = Field(description="The date of the event in YYYY-MM-DD format")
    participants: List[str] = Field(description="List of people attending the event")
    priority: str = Field(description="Priority level: High, Medium, or Low", pattern="^(High|Medium|Low)$")
    summary: str = Field(description="A brief 1-sentence summary of the event intent")

# --- 2. The Extraction Logic ---
def extract_event_details(text: str) -> Optional[CalendarEvent]:
    # Initialize the OpenAI client
    # Ensure you have OPENAI_API_KEY set in your environment or .env file
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found. Please set it in a .env file.")
        return None

    client = OpenAI(api_key=api_key)

    print(f"Analyzing text: '{text[:50]}...'")

    try:
        # We use the 'parse' method which is a helper for Structured Outputs
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06", # Supports Structured Outputs
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts calendar event details."},
                {"role": "user", "content": text},
            ],
            response_format=CalendarEvent, # Pass the Pydantic class directly!
        )

        # The SDK automatically validates and parses the JSON into our Pydantic model
        event_data = completion.choices[0].message.parsed
        return event_data

    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return None

# --- 3. Main Execution ---
if __name__ == "__main__":
    # Sample unstructured text (like an email or chat message)
    raw_text = """
    Hey team, just a reminder that we have the Q4 Marketing Strategy review 
    coming up next Tuesday, October 24th, 2025. 
    Alice, Bob, and Charlie need to be there. 
    This is super critical, we can't miss our targets.
    """

    result = extract_event_details(raw_text)

    if result:
        print("\n--- Extracted Structured Data ---")
        # We can access fields directly as Python attributes
        print(f"Event: {result.event_name}")
        print(f"Date:  {result.date}")
        print(f"Who:   {', '.join(result.participants)}")
        print(f"Level: {result.priority}")
        
        print("\n--- Full JSON Output ---")
        print(result.model_dump_json(indent=2))
