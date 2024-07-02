from pydantic_settings import BaseSettings, SettingsConfigDict

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


settings = Settings(_env_file='prod.env', _env_file_encoding='utf-8')