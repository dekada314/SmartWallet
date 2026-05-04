from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve()
while ROOT_DIR.name != "SmartWallet":
    ROOT_DIR = ROOT_DIR.parent


class RedisConfig(BaseSettings):
    host: str
    port: int
    db: int
    key_prefix: str
    password: None | SecretStr = None

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="REDIS_", case_sensitive=True, extra="ignore"
    )

    def get_url(self) -> str:
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


redis_config = RedisConfig()
