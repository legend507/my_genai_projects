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
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(message)s')
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

EMAIL_SUBJECT = "Your Daily Market Research Briefing + Reddit Trends"


def run_morning_stock_research() -> str:
    """Sends predefined prompts to a LLM, and emails the compiled research report.
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
    report_html = "<h1>Morning Stock Market Research</h1>"
    for item in research_prompts:
        topic = item["topic"]
        prompt = item["prompt"]
        
        # Get the analysis from Gemini
        response_text = send_prompts_to_gemini(client, model_to_use, config, prompt)

        # Convert Markdown to HTML for better formatting
        formatted_response = markdown.markdown(response_text)
        
        # Append to the HTML report
        report_html += f"<h2>{topic}</h2>"
        report_html += f"<p><strong>Prompt:</strong> {prompt}</p>"
        # Using <pre> tag to preserve formatting from the model's response
        report_html += (
            '<div style="background:#f5f5f5;padding:15px;border-radius:8px;'
            'font-family:monospace;white-space:pre-wrap;word-break:break-word;">'
            f"{formatted_response}</div>"
        )
        report_html += "<hr>"

    logging.info("run_morning_stock_research agent has finished its work.")
    return report_html

def run_trend_watcher() -> str:
    """Fetches trending posts from Reddit and sends them to specified LLM for analysis.
    """
    logging.info("Starting TrendWatcher and ChatGPT integration...")
    watcher = TrendWatcher()

    # Get top 50 posts from r/wallstreetbets.
    top_reddit_posts = watcher.get_trendy_reddit_posts(subreddit="wallstreetbets", count=50)
    
    # Format the posts into a single prompt.
    formatted_posts = "\n".join(
        [f"{i+1}. {post['title']} (Scores: {post['score']}) (URL: {post['url']}) (comments: {post['comments']})" for i, post in enumerate(top_reddit_posts)]
    )
    prompt = (
        "Summarize the following Reddit posts from r/wallstreetbets, "
        "and tell me what investment insights or advice can you provide?\n\n"
        f"{formatted_posts}"
    )
    logging.info(f"Sdnding prompt to Gemini: {prompt[:100]}...")

    # Send those posts to Gemini.
    model_to_use = 'gemini-2.5-pro'  # Latest pro model as of Aug 2025.
    client = genai.Client(api_key=GEMINI_API_KEY)
    grounding_tool = types.Tool(google_search =types.GoogleSearch())
    config = types.GenerateContentConfig(
        tools=[grounding_tool]
    )
    gemini_response = send_prompts_to_gemini(client, model_to_use, config, prompt_text=prompt)
    formatted_response = markdown.markdown(gemini_response)
    report_html = "<h1>TrendWatcher Analysis</h1>"
    report_html += f"<h2>Reddit Top 50 Trending Posts</h2>"
    report_html += f"<p><strong>Prompt:</strong> {prompt}</p>"
    report_html += (
            '<div style="background:#f5f5f5;padding:15px;border-radius:8px;'
            'font-family:monospace;white-space:pre-wrap;word-break:break-word;">'
            f"{formatted_response}</div>"
        )
    report_html += "<hr>"
    logging.info("run_trend_watcher agent has finished its work.")
    return report_html

@functions_framework.cloud_event
def main(cloud_event: CloudEvent):
    stock_report_html = run_morning_stock_research()
    trend_watcher_report = run_trend_watcher()

    # Concatenate all reports and send via email.
    full_report_html = stock_report_html + trend_watcher_report
    send_email(EMAIL_SUBJECT, full_report_html)

    logging.info("Main function execution completed.")
