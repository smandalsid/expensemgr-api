from dotenv import load_dotenv
import os

load_dotenv()

REDIS_CONN_STR = os.getenv("REDIS_CONN_STR")
UPSTASH_REDIS_REST_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_REDIS_REST_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")
