import logging
import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv


# Configure the logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(message)s')

# Load environment variables from a .env file
load_dotenv()

# --- Configuration ---
# From my corp account, intercom-connector-prod project.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def send_prompts_to_gemini(client, model_to_use, config, prompt_text, url_grounding = False) -> str:
    """
    Sends a single prompt to the Gemini API using a model configured for deep research.

    Args:
        prompt_text (str): The detailed prompt to send.

    Returns:
        str: The text response from Gemini.
    """
    logging.info(f"Sending prompt for: {prompt_text[:50]}...")
    if not client:
        client = genai.Client(api_key=GEMINI_API_KEY)
    if not model_to_use:
        model_to_use = "gemini-3-pro-preview"  # Latest pro preview model as of Nov 2025.
    if not config:
        # If url is in prompts, use grounding_tool, else use google search tool.
        if url_grounding:
            grounding_tool = {"url_context": {}}
        else:
            grounding_tool = types.Tool(google_search =types.GoogleSearch())
        config = types.GenerateContentConfig(
            tools=[grounding_tool]
        )
    try:
        # The metaprompt instructs the model on how to behave.
        metaprompt = (
            "Respond in markdown format and include source links and dates. "
            "Structure your response clearly. Where possible, outline your reasoning step-by-step. Avoid speculative language and focus on publicly known information and logical inferences.\n\n"
            f"Request: {prompt_text}"
        )
        
        response = client.models.generate_content(
            model = model_to_use,
            contents = metaprompt,
            config=config)
        logging.info("...Response received.")
        return response.text
    except Exception as e:
        logging.error(f"An error occurred while calling the Gemini API: {e}")
        return f"Error generating response for prompt: {prompt_text}"


def send_prompts_to_gemini_deep_research_agent(
    prompt_text: str,
    client=None,
    agent_name: str = None,
    agent_config: dict = None,
    tools: list = None,
    previous_interaction_id: str = None,
    poll_interval_seconds: int = 50,
    timeout_seconds: int = 900,
) -> str:
    """
    Sends a prompt to Gemini's Deep Research agent and waits for the final report.

    This function follows the Gemini Deep Research guide and intentionally does
    not use collaborative planning. If the caller passes
    `collaborative_planning` inside `agent_config`, it will be removed.

    Args:
        prompt_text (str): The research request to send to the Deep Research agent.
        client: Optional preconfigured `genai.Client`.
        agent_name (str): Optional Deep Research agent name. Defaults to the current
            preview agent.
        agent_config (dict): Optional Deep Research agent config.
        tools (list): Optional list of tool definitions for the interaction.
        previous_interaction_id (str): Optional interaction id for follow-up turns.
        poll_interval_seconds (int): Poll interval while waiting for completion.
        timeout_seconds (int): Max time to wait before failing.

    Returns:
        str: The final text output from the Deep Research agent.
    """
    logging.info(f"Sending deep research prompt for: {prompt_text[:50]}...")

    if not client:
        client = genai.Client(api_key=GEMINI_API_KEY)

    if not agent_name:
        agent_name = "deep-research-preview-04-2026"

    clean_agent_config = {"type": "deep-research"}
    if agent_config:
        clean_agent_config.update(agent_config)
    clean_agent_config.pop("collaborative_planning", None)

    interaction_kwargs = {
        "input": prompt_text,
        "agent": agent_name,
        "background": True,
        "store": True,
    }
    if clean_agent_config:
        interaction_kwargs["agent_config"] = clean_agent_config
    if tools is not None:
        interaction_kwargs["tools"] = tools
    if previous_interaction_id:
        interaction_kwargs["previous_interaction_id"] = previous_interaction_id

    try:
        interaction = client.interactions.create(**interaction_kwargs)
        logging.info(f"Deep research interaction started: {interaction.id}")

        started_at = time.time()
        while True:
            interaction = client.interactions.get(interaction.id)
            status = getattr(interaction, "status", None)
            logging.info(f"Deep research interaction {interaction.id} status: {status}")

            if status == "completed":
                outputs = getattr(interaction, "outputs", None) or []
                if outputs and getattr(outputs[-1], "text", None):
                    logging.info("...Deep research response received.")
                    return outputs[-1].text

                text_outputs = [
                    output.text
                    for output in outputs
                    if getattr(output, "type", None) == "text" and getattr(output, "text", None)
                ]
                if text_outputs:
                    logging.info("...Deep research response received from text outputs.")
                    return "\n\n".join(text_outputs)

                logging.warning("Deep research interaction completed with no text output.")
                return "Deep research completed, but no text output was returned."

            if status == "failed":
                error_message = getattr(interaction, "error", "Unknown Deep Research error")
                logging.error(f"Deep research interaction failed: {error_message}")
                return f"Error generating deep research response: {error_message}"

            if time.time() - started_at > timeout_seconds:
                logging.error(
                    f"Deep research interaction timed out after {timeout_seconds} seconds: {interaction.id}"
                )
                return (
                    "Error generating deep research response: "
                    f"timed out after {timeout_seconds} seconds."
                )

            time.sleep(poll_interval_seconds)
    except Exception as e:
        logging.error(f"An error occurred while calling the Gemini Deep Research agent: {e}")
        return f"Error generating deep research response for prompt: {prompt_text}"

if __name__ == "__main__":
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt_text = (
        "From the perspective of a financial analyst, "
        "go through the following stock tickers and tell me if there are any recent news, trends, or social media discussions that could impact their stock price"
        "AAPL, MSFT, GOOGL. Please provide a summary of the sentiment and any relevant links."
    )

    final_report_text = send_prompts_to_gemini_deep_research_agent(client=client, prompt_text=prompt_text)
    print(final_report_text)
