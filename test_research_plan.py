import os
import asyncio
import sys

# Add backend to sys.path if not already there to ensure imports work
# This assumes the script is run from the root of the repository
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from backend.app.clients.gemini_client import GeminiClient
from backend.api.endpoints.research_tree import _generate_research_plan

async def main():
    # Set the API key as an environment variable
    os.environ["GEMINI_API_KEY"] = "AIzaSyBGkZZT8yLLxDH_0p9cPxRIaRunH3vNI-c" # User's API Key

    natural_query = "To understand the methodologies, applications, and evaluation strategies for fine-tuning Large Language Models (LLMs) to perform effectively within specific domains."
    max_q = 5

    # Ensure the API key is set before instantiating the client
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        return
    
    print(f"Using GEMINI_API_KEY: {api_key[:5]}...{api_key[-4:]}") # Print partial key for confirmation

    try:
        gemini_client = GeminiClient() # API key is loaded from env var
        
        print("GeminiClient instantiated.") # Debug print
        
        # _generate_research_plan is an async function
        print("Calling _generate_research_plan...") # Debug print
        research_goal, queries = await _generate_research_plan(natural_query, gemini_client, max_q)
        print("_generate_research_plan call finished.") # Debug print
        
        print("\n--- Test Results ---")
        print(f"Research Goal: {research_goal}")
        print("Generated Queries:")
        if queries:
            for i, (query, description) in enumerate(queries):
                print(f"  {i+1}. Query: {query}")
                print(f"     Description: {description}")
        else:
            print("  No queries generated.")
        print("--- End of Test Results ---")

    except Exception as e:
        print(f"An error occurred during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
