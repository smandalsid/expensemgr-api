from dotenv import load_dotenv
import os

load_dotenv()

REDIS_CONN_STR = os.getenv("REDIS_CONN_STR")