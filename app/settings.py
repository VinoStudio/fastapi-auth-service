import bcrypt
from pydantic_settings import BaseSettings
from pydantic import EmailStr
from typing import Optional, Union, List, Annotated
from pathlib import Path
import config
import bcrypt


BASE_DIR = Path(__file__).parent.resolve().parent


class RSASettings:
    private_key_path: Path = BASE_DIR / "certificate" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certificate" / "jwt-public.pem"
    certificate: Path = BASE_DIR / "certificate" / "cert.pem"
    access_token_expire_minutes: int = 60 * 24
    refresh_token_expire_minutes: int = 60 * 24 * 7
    verify_token_expire_minutes: int = 60
    algorithm: str = "RS256"


class SMTPSettings:
    host: str = config.SMTP_HOST
    port: int = config.SMTP_PORT
    user: EmailStr = config.SMTP_USER
    password: str = config.SMTP_PASS

    @property
    def url(self):
        return f"smtp://{self.user}:{self.password}@{self.host}:{self.port}"


class RedisSettings:
    host: str = config.REDIS_HOST
    port: int = config.REDIS_PORT
    url: str = f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}/0"


class Settings(BaseSettings):
    db_url: str = (
        f"postgresql+asyncpg://{config.DB_USER}:{config.DB_PASS}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
    )
    db_echo: bool = True
    rsa: RSASettings = RSASettings()
    redis: RedisSettings = RedisSettings()
    smtp: SMTPSettings = SMTPSettings()


class TestSettings(BaseSettings):
    test_db_url: str = (
        f"postgresql+asyncpg://{config.TEST_DB_USER}:{config.TEST_DB_PASS}@{config.TEST_DB_HOST}:{config.TEST_DB_PORT}/{config.TEST_DB_NAME}"
    )
    test_db_echo: bool = True
    rsa: RSASettings = RSASettings()
    rsa.access_token_expire_minutes = 1


settings = Settings()
test_settings = TestSettings()
