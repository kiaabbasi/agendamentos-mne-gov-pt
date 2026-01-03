from setings import TelegramBotSetting, APISetting

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)
import threading
from telegram.request import HTTPXRequest
from telegram.constants import ParseMode

from UserManager import add_user, update_user, delete_user, get_all_users, get_user, User

from fastapi import FastAPI, Header, HTTPException, Depends, status

from colorama import init
init()

# -------------------- تنظیمات Bot --------------------
token = TelegramBotSetting.token
telgran_chanel = TelegramBotSetting.chanel1

if token is None:
    raise ValueError("Token must be str please check the setting and TELEGRAM_BOT_API_TOKEN in .env ")
if telgran_chanel is None:
    raise ValueError("telgran_chanel must be str please check the setting and TELEGRAM_CHANNEL_FOR_RESULTS in .env ")

proxy_url = "http://127.0.0.1:10001"  # یا socks5://...
app = (
    ApplicationBuilder()
    .token(token)
    .proxy(proxy_url)               # برای API requests
    .get_updates_proxy(proxy_url)   # برای polling (آپدیت‌ها)
    .build()
)



# -------------------- Add User --------------------
ADD_USERNAME, ADD_PASSWORD, ADD_CONSULAR_POST, ADD_CATEGORY, ADD_CONSULAR_ACT = range(5)
adding_user = {}

async def add_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return ConversationHandler.END
    user_id = update.message.from_user.id
    adding_user[user_id] = {}
    await update.message.reply_text("Enter username:")
    return ADD_USERNAME

async def add_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return ConversationHandler.END
    user_id = update.message.from_user.id
    username = update.message.text.strip()
    
    if get_user(username):
        await update.message.reply_text("❌ This username already exists. Please enter another username:")
        return ADD_USERNAME
    
    adding_user[user_id]['username'] = username
    await update.message.reply_text("Enter password:")
    return ADD_PASSWORD

async def add_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return ConversationHandler.END
    user_id = update.message.from_user.id
    adding_user[user_id]['password'] = update.message.text.strip()
    await update.message.reply_text("Enter consular post:")
    return ADD_CONSULAR_POST

async def add_consular_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return ConversationHandler.END
    user_id = update.message.from_user.id
    adding_user[user_id]['consular_post'] = update.message.text.strip()
    await update.message.reply_text("Enter category of consular act:")
    return ADD_CATEGORY

async def add_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return ConversationHandler.END
    user_id = update.message.from_user.id
    adding_user[user_id]['category_of_consular_act'] = update.message.text.strip()
    await update.message.reply_text("Enter consular act:")
    return ADD_CONSULAR_ACT

async def add_consular_act(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return ConversationHandler.END
    user_id = update.message.from_user.id
    user_data = adding_user[user_id]
    user_data['consular_act'] = update.message.text.strip()
    u=User(username=user_data['username'],
        password=user_data['password'],
        consular_post=user_data['consular_post'],
        category_of_consular_act=user_data['category_of_consular_act'],
        consular_act=user_data['consular_act'])
    # ثبت کاربر
    add_user(u)
    
    await update.message.reply_text(
        f"✅ User <b>{user_data['username']}</b> added successfully!",
        parse_mode=ParseMode.HTML
    )
    
    adding_user.pop(user_id, None)
    return ConversationHandler.END

async def cancel_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        user_id = update.message.from_user.id
        adding_user.pop(user_id, None)
        await update.message.reply_text("❌ Add user cancelled.")
    return ConversationHandler.END

add_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^➕ Add User$"), add_user_start)],
    states={
        ADD_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_username)],
        ADD_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_password)],
        ADD_CONSULAR_POST: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_consular_post)],
        ADD_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_category)],
        ADD_CONSULAR_ACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_consular_act)],
    },
    fallbacks=[CommandHandler("cancel", cancel_add)],
    per_user=True
)


# -------------------- Delete User --------------------
delete_user_sessions = {}

async def delete_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None or query.data is None:
        raise ValueError("CallbackQuery is None")
    await query.answer()
    
    username = query.data.split("_", 1)[1]
    user = get_user(username)
    if not user:
        await query.message.reply_text("User not found.")
        return ConversationHandler.END
    
    delete_user_sessions[query.from_user.id] = username
    
    keyboard = [
        [InlineKeyboardButton("✅ Confirm", callback_data="confirm_delete"),
         InlineKeyboardButton("❌ Cancel", callback_data="cancel_delete")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        f"Are you sure you want to delete user: <b>{username}</b> ?",
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )
    return 0  # ConversationHandler state

async def handle_delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None or query.data is None:
        return ConversationHandler.END
    await query.answer()
    
    user_id = query.from_user.id
    username = delete_user_sessions.get(user_id)
    if not username:
        await query.message.reply_text("No delete session found.")
        return ConversationHandler.END
    
    data = query.data
    if data == "confirm_delete":
        delete_user(username)
        await query.message.reply_text(f"User <b>{username}</b> deleted successfully ✅", parse_mode=ParseMode.HTML)
    else:
        await query.message.reply_text("Delete cancelled ❌")
    
    delete_user_sessions.pop(user_id, None)
    return ConversationHandler.END

# -------------------- ConversationHandler Delete --------------------
delete_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(delete_user_start, pattern=r"^delete_")],
    states={0: [CallbackQueryHandler(handle_delete_callback, pattern=r"confirm_delete|cancel_delete")]},
    fallbacks=[CommandHandler("cancel", lambda u,c: ConversationHandler.END)],
    per_user=True
)


# -------------------- Edit User --------------------
PASSWORD, CONSULAR_POST, CATEGORY, CONSULAR_ACT = range(4)
editing_user = {}

async def edit_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None or query.data is None:
        raise ValueError("CallbackQuery is None")
    await query.answer()
    username = query.data.split("_", 1)[1]
    user = get_user(username)
    if not user:
        await query.message.reply_text("User not found.")
        return ConversationHandler.END
    editing_user[query.from_user.id] = {
        "username": user.username,
        "password": user.password,
        "consular_post": user.consular_post,
        "category_of_consular_act": user.category_of_consular_act,
        "consular_act": user.consular_act,
        "field_editing": None
    }
    await show_edit_menu(query.message, query.from_user.id)
    return PASSWORD

async def show_edit_menu(message, user_id):
    user_data = editing_user[user_id]
    keyboard = [
        [InlineKeyboardButton("Password", callback_data="field:password"),
         InlineKeyboardButton("Consular Post", callback_data="field:consular_post")],
        [InlineKeyboardButton("Category", callback_data="field:category_of_consular_act"),
         InlineKeyboardButton("Consular Act", callback_data="field:consular_act")],
        [InlineKeyboardButton("Done", callback_data="done"),
         InlineKeyboardButton("Cancel", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        f"Editing user: <b>{user_data['username']}</b>\n"
        f"Password: <span class=\"tg-spoiler\">{user_data['password']}</span>\n"
        f"Consular Post: {user_data['consular_post']}\n"
        f"Category: {user_data['category_of_consular_act']}\n"
        f"Consular Act: {user_data['consular_act']}\n\n"
        "Select a field to edit:"
    )
    await message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

async def edit_field_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None or query.data is None:
        raise ValueError("CallbackQuery is None")
    await query.answer()
    user_id = query.from_user.id
    user_data = editing_user.get(user_id)
    if not user_data:
        await query.message.reply_text("No editing session found.")
        return ConversationHandler.END
    data = query.data
    if data == "done":
        update_user(
            username=user_data['username'],
            password=user_data['password'],
            consular_post=user_data['consular_post'],
            category_of_consular_act=user_data['category_of_consular_act'],
            consular_act=user_data['consular_act']
        )
        await query.message.reply_text("User updated successfully ✅")
        editing_user.pop(user_id, None)
        return ConversationHandler.END
    if data == "cancel":
        await query.message.reply_text("Edit cancelled ❌")
        editing_user.pop(user_id, None)
        return ConversationHandler.END
    field = data.split(":")[1]
    user_data['field_editing'] = field
    await query.message.reply_text(f"Enter new value for <b>{field.replace('_',' ').title()}</b>:", parse_mode=ParseMode.HTML)
    return PASSWORD

async def receive_new_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data = editing_user.get(user_id)
    if not user_data or not user_data['field_editing']:
        return
    field = user_data['field_editing']
    new_value = update.message.text.strip()
    user_data[field] = new_value
    user_data['field_editing'] = None
    await update.message.reply_text(f"<b>{field.replace('_',' ').title()}</b> updated successfully ✅", parse_mode=ParseMode.HTML)
    await show_edit_menu(update.message, user_id)
    return PASSWORD

edit_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_user_start, pattern=r"^edit_")],
    states={
        PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_new_value)]
    },
    fallbacks=[CommandHandler("cancel", lambda u,c: ConversationHandler.END)],
    per_user=True
)


# -------------------- Helper --------------------
async def send_result_to_chanel(txt: str):
    global app
    await app.bot.send_message(str(telgran_chanel), txt)

# -------------------- Start --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:        
        keyboard = [
            [KeyboardButton("➕ Add User"),KeyboardButton("📃 List Users")],
        ]
        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await update.message.reply_text("Welcome", reply_markup=reply_markup)

# -------------------- List Users --------------------
async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    users = get_all_users()
    if not users:
        await update.message.reply_text("No users found.")
        return

    for user in users:
        keyboard = [
            [
                InlineKeyboardButton("✏️ Edit User", callback_data=f"edit_{user.username}"),
                InlineKeyboardButton("❌ Delete User", callback_data=f"delete_{user.username}"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        is_registred_text = "Yes" if user.is_registred else "No"
        await update.message.reply_text(
            f"<b>{user.username}</b>\n{user.category_of_consular_act}-{user.consular_act}\nRegistered: {is_registred_text}\nPassword: <span class=\"tg-spoiler\">{user.password}</span>",
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

# -------------------- Handle Menu --------------------
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    text = update.message.text
    if text == "📃 List Users":
        await list_users(update, context)
    else:
        await update.message.reply_text("Unknown command")


# -------------------- Register Handlers --------------------
app.add_handler(edit_conv)
app.add_handler(CallbackQueryHandler(edit_field_callback, pattern=r"^field:|done|cancel"))
app.add_handler(delete_conv)
app.add_handler(add_conv)
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))

# -------------------- اجرای Bot در Thread --------------------
bot_thread = threading.Thread(target=app.run_polling)
bot_thread.start()
print("Bot is running...")

# -------------------- FastAPI --------------------
fapp = FastAPI()

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != APISetting.secret_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

@fapp.get("/send")
async def send(message: str, api_key: str = Depends(verify_api_key)):
    try:
        await send_result_to_chanel(message)
        return {"status": 200, "message": "sent"}
    except Exception as e:
        return {"status": 400, "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    print(f"FastAPI روی http://{APISetting.address}:{APISetting.port} در حال اجراست...")
    uvicorn.run(fapp, host=APISetting.address, port=APISetting.port)
