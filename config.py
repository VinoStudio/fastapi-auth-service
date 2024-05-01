from dotenv import load_dotenv
import os
import pathlib

BASE_DIR = pathlib.Path(__file__).parent.resolve()

load_dotenv(dotenv_path=BASE_DIR / ".env")

DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")

TEST_DB_HOST = os.getenv("POSTGRES_TEST_HOST")
TEST_DB_PORT = os.getenv("POSTGRES_TEST_PORT")
TEST_DB_USER = os.getenv("POSTGRES_TEST_USER")
TEST_DB_PASS = os.getenv("POSTGRES_TEST_PASSWORD")
TEST_DB_NAME = os.getenv("POSTGRES_TEST_DB")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")


SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASSWORD")
SMTP_PORT = os.getenv("SMTP_PORT")

print(SMTP_PASS)
