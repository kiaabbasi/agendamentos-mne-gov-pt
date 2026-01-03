from dotenv import load_dotenv
import os
from dataclasses import dataclass

basepath="D:\\python codes\\agendamentos-mne-gov-pt\\"

load_dotenv(f"{basepath}.env")

DEBUG = os.getenv("DEBUG") == "True"
VOICE_TO_TXT_API_KEY  = os.getenv("VOICE_TO_TXT_API_KEY") #https://eu1.asr.api.speechmatics.com/v2 
TELEGRAM_BOT_API_TOKEN=os.getenv("TELEGRAM_BOT_API_TOKEN")
TELEGRAM_CHANNEL_FOR_RESULTS = os.getenv("TELEGRAM_CHANNEL_FOR_RESULTS")


    
@dataclass(frozen=True)
class PageHandlerSetting():
    API_BASE_URL="http://127.0.0.1:8000/"
    secret_key = "kamciroqpogh34" 
    max_month_check=6
    
@dataclass(frozen=True)    
class APISetting:
    port=8000
    address="127.0.0.1"
    secret_key = "kamciroqpogh34" 
@dataclass(frozen=True) 
class TelegramBotSetting :
    token=TELEGRAM_BOT_API_TOKEN
    chanel1=TELEGRAM_CHANNEL_FOR_RESULTS
    
    
@dataclass(frozen=True)
class UserManagerSetting:
    database_name="database.sqllite3"