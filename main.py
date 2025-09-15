from trend_watcher.trend_watcher import TrendWatcher
from morning_stock_research.chatgpt import ask_chatgpt_with_search
from morning_stock_research.gemini import send_prompts_to_gemini
import logging
from google import genai
from google.genai import types

import os
from dotenv import load_dotenv

load_dotenv()

# Configure the logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(message)s')


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


if __name__ == "__main__":
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
