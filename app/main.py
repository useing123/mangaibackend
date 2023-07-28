import os

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

import openai
from dotenv import load_dotenv

from app.auth.router import router as auth_router
from app.manga_text.router import router as manga_text_router
from app.config import client, env, fastapi_config


app = FastAPI(**fastapi_config)

load_dotenv()
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")
IMGUR_CLIENT_SECRET = os.getenv("IMGUR_CLIENT_SECRET")


@app.on_event("shutdown")
def shutdown_db_client():
    client.close()


@app.on_event("startup")
def initialize_openai():
    openai.api_key = os.getenv("OPENAI_API_KEY")
    # replicate_api_key = os.getenv('REPLICATE_API_KEY')
    # replicate_api_key.REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
    # imgur_client_id.IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")
    # imgur_client_secret.IMGUR_CLIENT_SECRET = os.getenv("IMGUR_CLIENT_SECRET")


app.add_middleware(
    CORSMiddleware,
    allow_origins=env.CORS_ORIGINS,
    allow_methods=env.CORS_METHODS,
    allow_headers=env.CORS_HEADERS,
    allow_credentials=True,
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(manga_text_router, prefix="/manga", tags=["Manga"])
