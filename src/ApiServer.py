
from setings import TelegramBotSetting,APISetting

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

import threading
from telegram.request import HTTPXRequest


token = TelegramBotSetting.token
telgran_chanel=TelegramBotSetting.chanel1
if token is None:
    raise ValueError("Token must be str please check the setting and TELEGRAM_BOT_API_TOKEN in .env ")
if telgran_chanel is None:
    raise ValueError("telgran_chanel must be str please check the setting and TELEGRAM_CHANNEL_FOR_RESULTS in .env ")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("سلام! 👋 من آنلاینم.")

async def send_result_to_chanel(txt:str):
    global app
    await app.bot.send_message(str(telgran_chanel),txt)

request = HTTPXRequest()#proxy='http://127.0.0.1:10001'
app = ApplicationBuilder().token(token).request(request).build()

app.add_handler(CommandHandler("start", start))


    
    
bot_thread = threading.Thread(target=app.run_polling)
bot_thread.start()
print("Bot is running...")



from fastapi import FastAPI,Header,HTTPException,Depends,status

fapp = FastAPI()
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != APISetting.secret_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

@fapp.get("/send")
async def send(message:str,api_key: str = Depends(verify_api_key)):
    try :
        await send_result_to_chanel(message)
        return {"status": 200, "message": "sent"}
    except Exception as e :
        return {"status": 400, "message": e}
    
    
if __name__ == "__main__":
    import uvicorn
    print(f"FastAPI روی http://{APISetting.address}:{APISetting.port} در حال اجراست...")
    uvicorn.run(fapp, host=APISetting.address, port=APISetting.port)