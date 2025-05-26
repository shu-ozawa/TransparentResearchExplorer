import os
import asyncio
import logging
import sys

# Add backend to sys.path if not already there to ensure imports work
# This assumes the script is run from the root of the repository
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from backend.app.clients.gemini_client import GeminiClient
from backend.api.endpoints.research_tree import _generate_research_plan

# Configure logging to see INFO messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Specifically set the logger for research_tree to INFO if it might be configured differently elsewhere
logger = logging.getLogger('backend.api.endpoints.research_tree')
logger.setLevel(logging.INFO)


async def main():
    # Set the API key as an environment variable
    os.environ["GEMINI_API_KEY"] = "AIzaSyBGkZZT8yLLxDH_0p9cPxRIaRunH3vNI-c" # User's API Key

    natural_query = "LLMを用いた材料の合成可能性の説明とその評価"
    max_q = 5

    # Ensure the API key is set before instantiating the client
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.error("Error: GEMINI_API_KEY environment variable not set.")
        return
    
    logging.info(f"Using GEMINI_API_KEY: {api_key[:5]}...{api_key[-4:]}")

    try:
        gemini_client = GeminiClient() # API key is loaded from env var
        
        logging.info("GeminiClient instantiated.")
        
        # _generate_research_plan is an async function
        logging.info("Calling _generate_research_plan...")
        research_goal, queries = await _generate_research_plan(natural_query, gemini_client, max_q)
        logging.info("_generate_research_plan call finished.")
        
        logging.info("\n--- Test Results ---")
        logging.info(f"Research Goal (Natural Query): {research_goal}")
        logging.info("Generated Queries:")
        if queries:
            for i, (query, description) in enumerate(queries):
                logging.info(f"  {i+1}. Query: {query}")
                logging.info(f"     Description: {description}")
        else:
            logging.info("  No queries generated.")
        logging.info("--- End of Test Results ---")

    except Exception as e:
        logging.error(f"An error occurred during testing: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
