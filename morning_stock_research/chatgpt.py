import logging

import os
from openai import OpenAI
from dotenv import load_dotenv

from prompts import research_prompts  # Import the research prompts from prompts.py


# Configure the logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(message)s')
# Load environment variables from a .env file
load_dotenv()


def ask_chatgpt_with_search(prompt_text):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.responses.create(
        model="gpt-4o",
        tools=[{"type": "web_search_preview"}],
        input=prompt_text
    )
    return response.output_text  # Includes citations and search-enhanced answer

if __name__ == "__main__":
    query = "What's the latest news regarding Trump?"
    result = ask_chatgpt_with_search(query)
    print("Results with search:", result)
