from openai import OpenAI
from environs import Env

# Get environmental variables specifically LLM key
env = Env()
env.read_env()

OPENAI_MODEL = "gpt-4.1-mini"
DEEPSEEK_MODEL = "deepseek-v4-flash"
EMBEDDING_MODEL = "text-embedding-3-small"

TOP_K_CHUNKS = 5

client = OpenAI(
    api_key=env.str("CHATGPT_API_KEY")
)

client_d = OpenAI(
    api_key=env.str("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

db_url=env.str("DUCKDB_URL_V5")