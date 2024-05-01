from email.message import EmailMessage
from email.utils import formataddr
from typing import Optional
from app.tasks.templates import verification_email_template
from app.settings import settings


def send_verification_email(email: str, username: str, token: str):
    print(email, username, token)
    msg = EmailMessage()
    msg["Subject"] = "Verify your account"
    msg["From"] = settings.smtp.user
    msg["To"] = email
    msg.set_content(
        verification_email_template(username, token),
        subtype="html",
    )
    return msg


def email_template(username: str, email: str):
    msg = EmailMessage()
    msg["Subject"] = f"Ваш отчёт {username}"
    msg["From"] = settings.smtp.user
    msg["To"] = email
    msg.set_content(
        f"""
        <h1 style="color:blue">Добро пожаловать, {username}!</h1>
        <h1 style="color:red line-height:1.5 ">Ваш отчёт, {username}!</h1>
        """,
        subtype="html",
    )
    return msg
