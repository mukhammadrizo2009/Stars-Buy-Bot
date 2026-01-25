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
    
    
class ADMIN_ADD:
    ADD = 1
    REMOVE = 2
    
    
class PAYMENT:
    CUSTOM_AMOUNT = 1

    
class ADMIN_IDS:
    SUPERADMIN_ID = int(os.getenv("SUPERADMIN_ID"))
     
     
class STAR:
    STAR_EDIT = 1
    

class CARD:
    NUMBER = 1
    TYPE = 2
    
CHANNEL_ID = os.getenv("CHANNEL_ID")
CHANNEL_LINK = os.getenv("CHANNEL_LINK")
  
config = Config()
register_states = RegisterStates()
topup_states = TOPUP_STATES()
admin = ADMIN_IDS()
add_admin = ADMIN_ADD()
payment = PAYMENT()
star = STAR()
card = CARD()