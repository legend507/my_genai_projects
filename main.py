from trend_watcher.trend_watcher import TrendWatcher
from morning_stock_research.chatgpt import ask_chatgpt_with_search
from morning_stock_research.gemini import send_prompts_to_gemini, send_email
import logging
from google import genai
from google.genai import types
import markdown
import os
from dotenv import load_dotenv

# For GCP Cloud Run Functions.
from cloudevents.http import CloudEvent
import functions_framework

from morning_stock_research.prompts import research_prompts  # Import the research prompts from prompts.py


load_dotenv()

# Configure the logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(message)s')


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def run_morning_stock_research():
    """
    Main function to run the research agent.
    """
    logging.info(f"Starting the morning stock market research agent...")
    
    # Set up the Gemini model, with Google Search tool enabled.
    client = genai.Client(api_key=GEMINI_API_KEY)
    grounding_tool = types.Tool(google_search =types.GoogleSearch())
    config = types.GenerateContentConfig(
        tools=[grounding_tool]
    )
    model_to_use = 'gemini-2.5-pro'  # Latest pro model as of Aug 2025.

    # 1. Gather research from Gemini for each prompt
    full_report_html = "<h1>Morning Stock Market Research</h1>"
    for item in research_prompts:
        topic = item["topic"]
        prompt = item["prompt"]
        
        # Get the analysis from Gemini
        response_text = send_prompts_to_gemini(client, model_to_use, config, prompt)

        # Convert Markdown to HTML for better formatting
        formatted_response = markdown.markdown(response_text)
        
        # Append to the HTML report
        full_report_html += f"<h2>{topic}</h2>"
        full_report_html += f"<p><strong>Prompt:</strong> {prompt}</p>"
        # Using <pre> tag to preserve formatting from the model's response
        full_report_html += (
            '<div style="background:#f5f5f5;padding:15px;border-radius:8px;'
            'font-family:monospace;white-space:pre-wrap;word-break:break-word;">'
            f"{formatted_response}</div>"
        )
        full_report_html += "<hr>"

    # 2. Send the compiled report via email
    email_subject = "Your Daily Market Research Briefing"
    send_email(email_subject, full_report_html)
    
    logging.info("Research agent has finished its work.")


def test_trend_watcher():
    logging.info("Starting TrendWatcher and ChatGPT integration...")
    watcher = TrendWatcher()

    # Get top 20 posts from r/wallstreetbets.
    top_reddit_posts = watcher.get_trendy_reddit_posts(subreddit="wallstreetbets", count=20)
    
    # Format the posts into a single prompt.
    formatted_posts = "\n".join(
        [f"{i+1}. {post['title']} (Scores: {post['score']}) (URL: {post['url']}) (comments: {post['comments']})" for i, post in enumerate(top_reddit_posts)]
    )
    prompt = (
        "Based on the following trending posts from r/wallstreetbets, "
        "what investment insights or advice can you provide?\n\n"
        f"{formatted_posts}"
    )
    logging.info(f"Sdnding prompt to Gemini: {prompt[:100]}...")
    
    # Send those tests to Gemini.
    model_to_use = 'gemini-2.5-pro'  # Latest pro model as of Aug 2025.
    client = genai.Client(api_key=GEMINI_API_KEY)
    grounding_tool = types.Tool(google_search =types.GoogleSearch())
    config = types.GenerateContentConfig(
        tools=[grounding_tool]
    )
    gemini_response = send_prompts_to_gemini(client, model_to_use, config, prompt_text=prompt)
    print(gemini_response)

@functions_framework.cloud_event
def main(cloud_event: CloudEvent):
    run_morning_stock_research()
