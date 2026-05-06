from urllib.parse import quote

from dotenv import find_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisConfig(BaseSettings):
    host: str
    port: int
    db: int
    key_prefix: str
    password: None | SecretStr = None

    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        env_prefix="REDIS_",
        extra="ignore",
    )

    def get_url(self) -> str:
        if self.password:
            password = quote(self.password.get_secret_value(), safe="")
            return f"redis://:{password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


redis_config = RedisConfig()
