import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google import genai
from google.genai import types
from dotenv import load_dotenv
import markdown  # Add this import at the top
from prompts import research_prompts  # Import the research prompts from prompts.py


# Configure the logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Load environment variables from a .env file
load_dotenv()

# --- Configuration ---
# From my corp account, intercom-connector-prod project.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_APP_PASSWORD = os.getenv("SENDER_APP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")


def send_prompts_to_gemini(client, model_to_use, config, prompt_text):
    """
    Sends a single prompt to the Gemini API using a model configured for deep research.

    Args:
        prompt_text (str): The detailed prompt to send.

    Returns:
        str: The text response from Gemini.
    """
    logging.info(f"Sending prompt for: {prompt_text[:50]}...")
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


def send_email(subject, body):
    """
    Sends an email using Gmail's SMTP server.

    Args:
        subject (str): The subject of the email.
        body (str): The HTML body of the email.
    """
    if not all([SENDER_EMAIL, SENDER_APP_PASSWORD, RECIPIENT_EMAIL]):
        logging.info("Email credentials are not fully configured in the .env file. Skipping email.")
        return

    logging.info(f"Preparing to send email to {RECIPIENT_EMAIL}...")
    
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject

    # Style the email body for better readability
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            h1 {{ color: #1a73e8; }}
            h2 {{ color: #4CAF50; border-bottom: 2px solid #f0f0f0; padding-bottom: 5px;}}
            p {{ margin-bottom: 15px; }}
            pre {{ background-color: #f5f5f5; padding: 15px; border-radius: 8px; white-space: pre-wrap; word-wrap: break-word; }}
        </style>
    </head>
    <body>
        {body}
    </body>
    </html>
    """
    msg.attach(MIMEText(html_body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        logging.info("Email sent successfully!")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")


def main():
    """
    Main function to run the research agent.
    """
    logging.info("Starting the morning stock market research agent...")
    
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


if __name__ == "__main__":
    main()
