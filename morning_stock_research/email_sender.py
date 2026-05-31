import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv


load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_APP_PASSWORD = os.getenv("SENDER_APP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")


def send_email(subject: str, body: str) -> None:
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
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = subject

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
    msg.attach(MIMEText(html_body, "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        logging.info("Email sent successfully!")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
