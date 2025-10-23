from trend_watcher.trend_watcher import TrendWatcher
from morning_stock_research.chatgpt import ask_chatgpt_with_search
from morning_stock_research.gemini import send_prompts_to_gemini, send_email
from sheet_reader.sheet_reader import GoogleSheetReader
import logging
from google import genai
from google.genai import types
import markdown
import os
from dotenv import load_dotenv

# For GCP Cloud Run Functions.
from cloudevents.http import CloudEvent
import functions_framework

# Import predefined prompts.
from morning_stock_research.prompts import research_prompts
from trend_watcher.prompts import trend_watcher_prompts
from sheet_reader.prompts import sheet_reader_prompts
from web_dashboards.prompts import url_resources

load_dotenv()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(message)s')
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

EMAIL_SUBJECT = "Your Daily Market Research Briefing + Reddit Trends"
GEMINI_MODEL_ID = "gemini-2.5-pro"  # Latest pro model as of Aug 2025.


def run_morning_stock_research() -> str:
    """Sends predefined prompts to a LLM, and emails the compiled research report.
    """
    logging.info(f"Starting the morning stock market research agent...")
    
    # 1. Gather research from Gemini for each prompt
    report_html = "<h1>Morning Stock Market Research</h1>"
    for item in research_prompts:
        topic = item["topic"]
        prompt = item["prompt"]
        
        # Get the analysis from Gemini
        response_text = send_prompts_to_gemini(None, None, None, prompt)

        # Convert Markdown to HTML for better formatting
        formatted_response = markdown.markdown(response_text, extensions=["tables"])
        
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
        [f"{i+1}. {post['title']} (Scores: {post['score']}) (URL: {post['url']}) \n\n" for i, post in enumerate(top_reddit_posts)]
    )
    prompt = (trend_watcher_prompts["reddit"] + f"{formatted_posts}")
    logging.info(f"Sdnding prompt to Gemini: {prompt[:100]}...")

    gemini_response = send_prompts_to_gemini(None, None, None, prompt_text=prompt)
    formatted_response = markdown.markdown(gemini_response, extensions=["tables"])
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

def run_sheet_reader() -> str: 
    """Reads my portfolio data from Google sheet and process.
    """
    logging.info("Starting Google Sheets reader...")
    # Get my holdings from sheet.
    sheet_be_richer = 'be_richer'
    creds_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 
        "./wordpress-hosting-302807-2a5d57c336dd.json"))
    reader = GoogleSheetReader(creds_path, sheet_be_richer)
    my_holdings = reader.read_my_current_holdings()

    # Title.
    report_html = "<h1>My Holdings Analysis</h1>"
    # Report 1, negative impact analysis.
    prompt = sheet_reader_prompts["my_holdings_negative_impact"] + f"\nHere is my current holdings data:\n{my_holdings.to_string(index=False)}"
    logging.info(f"Sending prompt to Gemini: {prompt[:100]}...")
    gemini_response = send_prompts_to_gemini(None, None, None, prompt_text=prompt)
    formatted_response = markdown.markdown(gemini_response, extensions=["tables"])
    report_html += f"<h2>Negative Impact Analysis</h2>"
    report_html += f"<p><strong>Prompt:</strong> {prompt}</p>"
    report_html += (
            '<div style="background:#f5f5f5;padding:15px;border-radius:8px;'
            'font-family:monospace;white-space:pre-wrap;word-break:break-word;">'
            f"{formatted_response}</div>"
        )
    report_html += "<hr>"
    # Report 2, down trend for the past 3 days.
    prompt = sheet_reader_prompts["my_holdings_down_trend_3days"] + f"\nHere is my current holdings data:\n{my_holdings.to_string(index=False)}"
    logging.info(f"Sending prompt to Gemini: {prompt[:100]}...")
    gemini_response = send_prompts_to_gemini(None, None, None, prompt_text=prompt)
    formatted_response = markdown.markdown(gemini_response, extensions=["tables"])
    report_html += f"<h2>Down Trend 3 Days Analysis</h2>"
    report_html += f"<p><strong>Prompt:</strong> {prompt}</p>"
    report_html += (
            '<div style="background:#f5f5f5;padding:15px;border-radius:8px;'
            'font-family:monospace;white-space:pre-wrap;word-break:break-word;">'
            f"{formatted_response}</div>"
        )
    report_html += "<hr>"

    logging.info("Google Sheets reader has finished its work.")
    return report_html

def run_politician_trades() -> str:
    """Fetches recent stock trades made by US Congress members and analyzes them.
    """
    logging.info("Starting Politician Trades Analysis...")
    # Example URL for politician trades.
    prompt = url_resources["prompts"] + ",".join(url_resources["well_known_politicians"])
    logging.info(f"Sending prompt to Gemini: {prompt[:100]}...")
    gemini_response = send_prompts_to_gemini(None, None, None, prompt_text=prompt, url_grounding=True)
    formatted_response = markdown.markdown(gemini_response, extensions=["tables"])
    report_html = "<h1>Politician Trades Analysis</h1>"
    report_html += f"<p><strong>Prompt:</strong> {prompt}</p>"
    report_html += (
            '<div style="background:#f5f5f5;padding:15px;border-radius:8px;'
            'font-family:monospace;white-space:pre-wrap;word-break:break-word;">'
            f"{formatted_response}</div>"
        )
    report_html += "<hr>"
    logging.info("Politician Trades Analysis has finished its work.")
    return report_html

@functions_framework.cloud_event
def main(cloud_event: CloudEvent):
    stock_report_html = run_morning_stock_research()
    trend_watcher_report = run_trend_watcher()
    sheet_reader_report = run_sheet_reader()
    politician_trades_report = run_politician_trades()

    # Concatenate all reports and send via email.
    full_report_html = (stock_report_html 
                        + trend_watcher_report 
                        + sheet_reader_report
                        + politician_trades_report)
    send_email(EMAIL_SUBJECT, full_report_html)

    logging.info("Main function execution completed.")
