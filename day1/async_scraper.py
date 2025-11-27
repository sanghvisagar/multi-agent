import asyncio
import aiohttp
from pydantic import BaseModel, HttpUrl, ValidationError
from typing import List, Optional
import time
import random

# --- 1. Define Data Structure with Pydantic ---
# Pydantic allows us to define the "shape" of our data. 
# In an AI context, this is exactly how we define what we want the LLM to return.
class ScrapedPage(BaseModel):
    url: HttpUrl
    status_code: int
    content_length: int
    title: Optional[str] = None
    
    # You can add custom validation logic here if needed

# --- 2. Async Function to Fetch Data ---
# 'async def' defines a coroutine. It can be paused and resumed.
async def fetch_page(session: aiohttp.ClientSession, url: str, semaphore: asyncio.Semaphore) -> Optional[ScrapedPage]:
    # Acquire a "token" from the semaphore. If limit is reached, this waits.
    async with semaphore:
        print(f"Starting fetch for: {url}")
        # Simple Retry Logic
        for attempt in range(3):
            try:
                # Simulate flaky network (20% chance of failure)
                if random.random() < 0.2:
                    print(f"Simulated network error for {url} (Attempt {attempt + 1})")
                    raise Exception("Simulated Network Error")

                # 'await' yields control back to the event loop while waiting for I/O
                async with session.get(url) as response:
                    content = await response.text()
                    
                    # Create and validate data using our Pydantic model
                    page_data = ScrapedPage(
                        url=url,
                        status_code=response.status,
                        content_length=len(content),
                        title=content[:50].strip() + "..." 
                    )
                    print(f"Finished fetch for: {url}")
                    return page_data
            
            except Exception as e:
                print(f"Error fetching {url}: {str(e)}")
                if attempt < 2:
                    wait_time = (attempt + 1) * 0.5 # Linear backoff
                    print(f"Retrying {url} in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"Given up on {url}")
                    return None

# --- 3. The Main Orchestrator ---
async def main():
    urls = [
        "https://www.python.org",
        "https://www.google.com",
        "https://www.github.com",
        "https://pypi.org",
        "https://docs.python.org",
    ]

    # Context manager for the HTTP session
    async with aiohttp.ClientSession() as session:
        # Create a Semaphore to limit concurrency to 2 requests at a time
        # This simulates an API rate limit (e.g., only 2 LLM calls allowed at once)
        sem = asyncio.Semaphore(2)
        
        tasks = []
        # Create a list of coroutine objects (tasks) but don't await them yet
        for url in urls:
            task = fetch_page(session, url, sem)
            tasks.append(task)
        
        print(f"--- Starting {len(urls)} requests concurrently ---")
        start_time = time.time()
        
        # asyncio.gather runs all tasks concurrently and waits for them to finish
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        print(f"--- All finished in {end_time - start_time:.2f} seconds ---")

        # Filter out None results (failed requests)
        valid_results = [r for r in results if r]
        
        print("\n--- Validated Results (Pydantic Models) ---")
        for res in valid_results:
            # Pydantic models have a nice string representation
            print(res)

# --- Entry Point ---
if __name__ == "__main__":
    asyncio.run(main())
