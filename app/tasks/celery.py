from celery import Celery
from app.database import db
from app.settings import settings
from app.tasks.email_utils import send_verification_email, email_template
import smtplib, ssl


celery = Celery(__name__, broker=settings.redis.url)
celery.conf.update(
    result_expires=60 * 60 * 24,  # 24 hours
    enable_utc=True,
    accept_content=["json", "pickle", "application/json"],
    smtp_host=settings.smtp.host,
    smtp_port=settings.smtp.port,
    smtp_user=settings.smtp.user,
    smtp_password=settings.smtp.password,
)


@celery.task
def send_verification_email_task(email: str, username: str, token: str):
    msg = send_verification_email(email, username, token)
    try:
        with smtplib.SMTP(settings.smtp.host, settings.smtp.port) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(settings.smtp.user, settings.smtp.password)
            server.send_message(msg)
    except Exception:
        raise Exception("Failed to send verification email")


@celery.task
def send_email(username: str, email: str):
    msg = email_template(username, email)
    try:
        with smtplib.SMTP(settings.smtp.host, settings.smtp.port) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(settings.smtp.user, settings.smtp.password)
            server.send_message(msg)
    except Exception as e:
        print(e)
        raise Exception("Failed to send verification email")
