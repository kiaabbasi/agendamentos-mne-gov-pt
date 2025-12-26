
from setings import TELEGRAM_BOT_API_TOKEN,TELEGRAM_CHANNEL_FOR_RESULTS,API_SERVER_SECRET_KEY

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

import threading
from telegram.request import HTTPXRequest


token = TELEGRAM_BOT_API_TOKEN
telgran_chanel=TELEGRAM_CHANNEL_FOR_RESULTS
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

request = HTTPXRequest(proxy='http://127.0.0.1:10001')
app = ApplicationBuilder().token(token).request(request).build()

app.add_handler(CommandHandler("start", start))


    
    
bot_thread = threading.Thread(target=app.run_polling)
bot_thread.start()
print("Bot is running...")
from fastapi import FastAPI,Header,HTTPException,Depends,status

fapp = FastAPI()
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_SERVER_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

@fapp.get("/send")
async def send(message:str,api_key: str = Depends(verify_api_key)):
    try :
        await send_result_to_chanel(message)
        return {"status": "sent", "message": message}
    except Exception as e :
        return {"status": "faild", "message": e}
    
    
if __name__ == "__main__":
    import uvicorn
    print("FastAPI روی http://127.0.0.1:8000 در حال اجراست...")
    uvicorn.run(fapp, host="127.0.0.1", port=8000)