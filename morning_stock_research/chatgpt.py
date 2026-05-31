import logging
import os
import time

from dotenv import load_dotenv
from openai import OpenAI


# Configure the logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(message)s",
)

# Load environment variables from a .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SINGLE_TURN_MODEL = "gpt-5-mini"
DEEP_RESEARCH_MODEL = "o3-deep-research"

class AskChatGPT:
    def __init__(self, client=None, api_key: str = OPENAI_API_KEY):
        self.client = client or OpenAI(api_key=api_key)

    def single_turn_query(
        self,
        prompt_text: str,
        model: str = SINGLE_TURN_MODEL,
        tools: list = None,
    ) -> str:
        """Send one prompt to ChatGPT and return the text response."""
        logging.info(f"Sending ChatGPT prompt for: {prompt_text[:50]}...")

        if tools is None:
            tools = [{"type": "web_search_preview"}]

        try:
            response = self.client.responses.create(
                model=model,
                tools=tools,
                input=prompt_text,
            )
            logging.info("...ChatGPT response received.")
            return response.output_text
        except Exception as e:
            logging.error(f"An error occurred while calling ChatGPT: {e}")
            return f"Error generating ChatGPT response for prompt: {prompt_text}"

    def deep_research_query(
        self,
        prompt_text: str,
        model: str = DEEP_RESEARCH_MODEL,
        tools: list = None,
        background: bool = True,
        poll_interval_seconds: int = 300,
        timeout_seconds: int = 900,
    ) -> str:
        """Send one prompt to OpenAI Deep Research and return the final report."""
        logging.info(f"Sending ChatGPT deep research prompt for: {prompt_text[:50]}...")

        if tools is None:
            tools = [{"type": "web_search_preview"}]

        try:
            response = self.client.responses.create(
                model=model,
                tools=tools,
                input=prompt_text,
                background=background,
            )

            if not background:
                logging.info("...ChatGPT deep research response received.")
                return response.output_text

            logging.info(f"Deep research response started: {response.id}")
            started_at = time.time()

            while True:
                response = self.client.responses.retrieve(response.id)
                status = getattr(response, "status", None)
                logging.info(f"Deep research response {response.id} status: {status}")

                if status == "completed":
                    logging.info("...ChatGPT deep research response received.")
                    return response.output_text

                if status in {"failed", "cancelled", "incomplete"}:
                    error = getattr(response, "error", None)
                    incomplete_details = getattr(response, "incomplete_details", None)
                    error_message = error or incomplete_details or "Unknown Deep Research error"
                    logging.error(f"Deep research response ended with status {status}: {error_message}")
                    return f"Error generating ChatGPT deep research response: {error_message}"

                if time.time() - started_at > timeout_seconds:
                    logging.error(
                        f"Deep research response timed out after {timeout_seconds} seconds: {response.id}"
                    )
                    return (
                        "Error generating ChatGPT deep research response: "
                        f"timed out after {timeout_seconds} seconds."
                    )

                time.sleep(poll_interval_seconds)
        except Exception as e:
            logging.error(f"An error occurred while calling ChatGPT Deep Research: {e}")
            return f"Error generating ChatGPT deep research response for prompt: {prompt_text}"


if __name__ == "__main__":
    query = "What's the latest news regarding Trump?"
    ask_chatgpt = AskChatGPT()
    result = ask_chatgpt.deep_research_query(prompt_text=query)
    print("Results:", result)
