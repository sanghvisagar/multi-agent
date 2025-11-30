import json
import time
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from termcolor import colored

# --- 1. The Blackboard (Shared State) ---
# This is the "Brain" of the system. All agents read/write to this.
class Blackboard(BaseModel):
    user_goal: str = ""
    research_notes: List[str] = []
    draft_content: str = ""
    review_feedback: str = ""
    final_output: str = ""
    
    # Metadata
    logs: List[str] = []

    def log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self.logs.append(entry)
        print(colored(entry, "white", attrs=["dark"]))

# --- 2. The Agents (Stateless Workers) ---
# Notice they take the Blackboard as input and return a MODIFIED Blackboard.

class ResearcherAgent:
    def run(self, state: Blackboard) -> Blackboard:
        state.log("Researcher: Starting research...")
        
        # Simulate finding info based on the goal
        if "python" in state.user_goal.lower():
            info = "Python is a high-level programming language."
        else:
            info = "General knowledge about the topic."
            
        state.research_notes.append(info)
        state.log(f"Researcher: Added note -> '{info}'")
        return state

class WriterAgent:
    def run(self, state: Blackboard) -> Blackboard:
        state.log("Writer: Drafting content...")
        
        if not state.research_notes:
            state.log("Writer: No research found! Cannot write.")
            return state
            
        # Combine notes into a draft
        notes_text = " ".join(state.research_notes)
        state.draft_content = f"Title: {state.user_goal}\nBody: {notes_text}\n(Drafted by AI)"
        state.log("Writer: Draft created.")
        return state

class ReviewerAgent:
    def run(self, state: Blackboard) -> Blackboard:
        state.log("Reviewer: Reviewing draft...")
        
        if not state.draft_content:
            state.log("Reviewer: No draft to review!")
            return state
            
        # Simulate a review
        if "Python" in state.draft_content:
            state.review_feedback = "Approved"
            state.final_output = state.draft_content + "\n[VERIFIED]"
        else:
            state.review_feedback = "Rejected: Missing key keywords."
            
        state.log(f"Reviewer: Feedback -> {state.review_feedback}")
        return state

# --- 3. The Controller (The Loop) ---
def run_system(goal: str):
    # Initialize Shared State
    state = Blackboard(user_goal=goal)
    
    # Initialize Agents
    researcher = ResearcherAgent()
    writer = WriterAgent()
    reviewer = ReviewerAgent()
    
    print(colored(f"--- Starting Mission: {goal} ---", "cyan"))
    
    # Step 1: Research
    state = researcher.run(state)
    
    # Step 2: Write
    state = writer.run(state)
    
    # Step 3: Review
    state = reviewer.run(state)
    
    # Final Output
    print(colored("\n--- Final State ---", "green"))
    print(f"Goal: {state.user_goal}")
    print(f"Final Output:\n{state.final_output}")
    print(f"Logs: {len(state.logs)} entries")

if __name__ == "__main__":
    run_system("Write a short post about Python")
