from dotenv import load_dotenv
import os
from dataclasses import dataclass

basepath="D:\\python codes\\agendamentos-mne-gov-pt\\"

load_dotenv("../.env")

DEBUG = os.getenv("DEBUG") == "True"
VOICE_TO_TXT_API_KEY  = os.getenv("VOICE_TO_TXT_API_KEY") #https://eu1.asr.api.speechmatics.com/v2 


@dataclass(frozen=True)
class AppConfig:
    api_url: str = "https://api.example.com"
    timeout: int = 10