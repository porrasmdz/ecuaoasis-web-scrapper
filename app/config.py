from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(".env"))
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    SHOPIFY_USER: str
    SHOPIFY_PASSWORD: str
    SHOPIFY_ADMIN_LINK: str
    ROOT_ABSOLUTE_PATH: str
    SH_API_URL: str
    SH_SHOP_NAME: str
    SH_API_TOKEN: str
    SH_API_KEY: str
    SH_API_SECRET_KEY: str
    GH_OWNER: str
    REPO: str
    BRANCH: str


settings = Settings(_env_file='prod.env', _env_file_encoding='utf-8')