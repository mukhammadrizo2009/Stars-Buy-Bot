import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")


class RegisterStates():
    NAME = 0
    PHONE_NUMBER =1
    CONFIRM = 2

class TOPUP_STATES:
    AMOUNT = 1
    CHECK = 2
    
class ADMIN_IDS:
    ADMIN = os.getenv("ADMIN_IDS")
        
config = Config()
register_states = RegisterStates()
topup_states = TOPUP_STATES()
admin = ADMIN_IDS()