import smtplib
from email.mime.text import MIMEText
import os
from app.utils.logger import logger

def send_feedback_email(subject: str, body: str):
    sender = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    recipient = os.getenv("FEEDBACK_RECEIVER_EMAIL")

    if not sender or not password or not recipient:
        raise ValueError(f"[환경변수 오류] sender={sender}, password={password}, recipient={recipient}")

    logger.info(f"[메일 전송] sender={sender}, recipient={recipient}, password={password[:4]}****")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)
