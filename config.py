from decouple import config
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = config("SQLALCHEMY_DATABASE_URL", default="postgresql+psycopg2://postgres:postgres@localhost:5432/todo")

JWT_ACCESS_TOKEN_EXPIRE_MINUTES = config("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=1440)
JWT_SECRET_KEY = config("JWT_SECRET_KEY", cast=str, default="ch4nge_menya_10_t1m3z!!!")

UVICORN_HOST = config("UVICORN_HOST", default="0.0.0.0")
UVICORN_PORT = config("UVICORN_PORT", cast=int, default=8000)
UVICORN_UDS = config("UVICORN_UDS", default=None)
UVICORN_SSL_CERTFILE = config("UVICORN_SSL_CERTFILE", default=None)
UVICORN_SSL_KEYFILE = config("UVICORN_SSL_KEYFILE", default=None)

DEBUG = config("DEBUG", default=False, cast=bool)
DOCS = config("DOCS", default=False, cast=bool)

FORWARDED_ALLOW_IPS = config(
    'FORWARDED_ALLOW_IPS',
    default="127.0.0.1",
    cast=lambda v: [address.strip() for address in v.split(',')] if v else []
)
