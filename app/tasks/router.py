from fastapi import APIRouter, status
from app.tasks.celery import send_email

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
def send_the_message(username: str, email: str):
    send_email.delay(username, email)
    return {"message": "Email sent"}
