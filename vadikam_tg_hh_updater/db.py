import os
import shelve

from dotenv import load_dotenv

load_dotenv()

TOKEN_REFRESH_URL = os.getenv('TOKEN_REFRESH_URL')
RESUME_URL = os.getenv('RESUME_URL')
NEGOTIATIONS_URL = os.getenv('NEGOTIATIONS_URL')

TOKEN_TYPE = os.getenv('TOKEN_TYPE')
FIRST_REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
FIRST_ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

telegram_token = os.getenv('TELEGRAM_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')
timeout = int(os.getenv('TIMEOUT'))

db = shelve.open('little_db', 'c')
