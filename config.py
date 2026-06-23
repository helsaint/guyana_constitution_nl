from openai import OpenAI
import os
from environs import Env

# Get environmental variables specifically LLM key
env = Env()
env.read_env()

OPENAI_MODEL = "gpt-4.1-mini"
EMBEDDING_MODEL = "text-embedding-3-small"

TOP_K_CHUNKS = 5

client = OpenAI(
    api_key=env.str("CHATGPT_API_KEY")
)

db_url=env.str("DUCKDB_URL")