import logging
import asyncio
import os
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters, 
    ConversationHandler
)
from telegram.error import Forbidden, RetryAfter

# ================= LOGGING =================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================= FLASK SERVER =================
app = Flask('')

@app.route('/')
def home():
    return "Bot is running and healthy!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True # থ্রেডটিকে ব্যাকগ্রাউন্ডে রাখবে
    t.start()

# ================= CONFIGURATION =================
# আপনার টোকেনটি সরাসরি এখানে না রেখে Render Environment Variable এ রাখা ভালো
BOT_TOKEN = os.getenv("BOT_TOKEN", "8525057709:AAEXv7b8l8tA9qb1KuCDtlv74d9LtaVWe1Q")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1146186608"))
REQUIRED_CHANNEL = int(os.getenv("REQUIRED_CHANNEL", "-1001481593780"))
CHANNEL_LINK = "https://t.me/+3U0nMzWs4Aw0YjFl"

# Media Links (Your Original Links)
IMAGE_URL_WELCOME = "https://i.ibb.co/XfxnhBYY/file-000000006ac47206b9a3e5b41d2e17e1.png"
IMAGE_URL_REG = "https://i.ibb.co/PZ5VTZVT/IMG-20260201-052425-386.jpg"
IMAGE_URL_SUCCESS = "https://i.ibb.co/fdwt2s8D/file-00000000973471faba7ce65cd5c96718.png"
IMAGE_URL_HACK_MENU = "https://i.ibb.co/C3YqyxJn/Data-Breach-at-Betting-Platform-1win-Exposed-96-Million-Users.png"

# Game Links
GAME_URLS = {
    'aviator': "https://aviatorbahohacker.fwh.is/",
    'mines': "https://mines-game-hack.netlify.app/",
}

USER_FILE = "users.txt"
WAITING_FOR_ID = 1
BROADCAST_SIMPLE = 2

# Languages
LANGUAGES = {
    'en': {'name': '🇺🇸 English', 'earn_btn': 'Start Earning', 'reg_btn': 'Registration', 'verify_btn': '✅ Verify ID', 'ask_id': 'Send 9-digit Account ID:', 'analyzing': '🔄 Verifying...', 'success_msg': '✅ <b>ACCOUNT VERIFIED!</b>', 'play_btn': '🎮 Play Hack'},
    'bd': {'name': '🇧🇩 Bangla', 'earn_btn': 'টাকা আয় শুরু করুন', 'reg_btn': 'রেজিস্ট্রেশন লিংক', 'verify_btn': '✅ ভেরিফাই করুন', 'ask_id': '৯ ডিজিটের আইডি দিন:', 'analyzing': '🔄 যাচাই করা হচ্ছে...', 'success_msg': '✅ <b>একাউন্ট ভেরিফাইড!</b>', 'play_btn': '🎮 হ্যাক দিয়ে খেলুন'},
}

# ================= UTILS =================
def save_user(user_id):
    if not os.path.exists(USER_FILE): open(USER_FILE, 'w').close()
    with open(USER_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USER_FILE, "a") as f: f.write(f"{user_id}\n")

def get_users():
    if not os.path.exists(USER_FILE): return []
    with open(USER_FILE, "r") as f: return f.read().splitlines()

async def check_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return member.status in [ChatMember.MEMBER, ChatMember.OWNER, ChatMember.ADMINISTRATOR]
    except Exception: return False

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)
    
    is_member = await check_membership(user_id, context)
    if is_member:
        return await send_language_menu(update, context)
    
    keyboard = [[InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
                [InlineKeyboardButton("✅ Joined / Verify", callback_data='check_join_status')]]
    await update.message.reply_text("⚠️ <b>Join Channel First!</b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

async def check_join_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if await check_membership(user_id, context):
        await query.answer("Success!")
        await send_language_menu(update, context)
    else:
        await query.answer("❌ You haven't joined yet!", show_alert=True)

async def send_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(v['name'], callback_data=f'lang_{k}') for k, v in LANGUAGES.items()]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = "Please select your language:"
    if update.callback_query: await update.callback_query.message.edit_text(msg, reply_markup=reply_markup)
    else: await update.message.reply_text(msg, reply_markup=reply_markup)

async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang_code = query.data.split('_')[1]
    context.user_data['selected_lang'] = lang_code
    lang_data = LANGUAGES[lang_code]
    keyboard = [[InlineKeyboardButton(lang_data['earn_btn'], callback_data='start_earning')]]
    await query.message.delete()
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=IMAGE_URL_WELCOME, caption=f"Language: {lang_data['name']}", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_registration_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang_code = context.user_data.get('selected_lang', 'en')
    lang_data = LANGUAGES[lang_code]
    info_text = "<b>Step 1: Register</b>\nUse Promo: <b>BLACK110</b>"
    keyboard = [[InlineKeyboardButton(lang_data['reg_btn'], url="https://1wezue.com/casino")],
                [InlineKeyboardButton(lang_data['verify_btn'], callback_data='verify_reg')]]
    await update.callback_query.message.delete()
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=IMAGE_URL_REG, caption=info_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def verify_process_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang_code = context.user_data.get('selected_lang', 'en')
    await update.callback_query.message.reply_text(LANGUAGES[lang_code]['ask_id'])
    return WAITING_FOR_ID

async def receive_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang_code = context.user_data.get('selected_lang', 'en')
    msg = await update.message.reply_text(LANGUAGES[lang_code]['analyzing'])
    await asyncio.sleep(2)
    await msg.delete()
    
    keyboard = [[InlineKeyboardButton(LANGUAGES[lang_code]['play_btn'], callback_data='play_hack_action')]]
    await update.message.reply_photo(photo=IMAGE_URL_SUCCESS, caption=LANGUAGES[lang_code]['success_msg'], parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
    return ConversationHandler.END

async def play_hack_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("✈️ Aviator", url=GAME_URLS['aviator'])],
                [InlineKeyboardButton("💣 Mines", url=GAME_URLS['mines'])]]
    await update.callback_query.message.delete()
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=IMAGE_URL_HACK_MENU, caption="Select Game:", reply_markup=InlineKeyboardMarkup(keyboard))

# ================= DEPLOYMENT =================
if __name__ == '__main__':
    # ১. ফ্লাস্ক সার্ভার চালু করা (Keep Alive)
    keep_alive()
    
    # ২. বট অ্যাপ্লিকেশন তৈরি
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()

    # কনভারসেশন হ্যান্ডলার
    verify_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(verify_process_start, pattern='^verify_reg$')],
        states={WAITING_FOR_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_id)]},
        fallbacks=[CommandHandler('cancel', lambda u, c: ConversationHandler.END)]
    )

    # হ্যান্ডলার অ্যাড করা
    app_bot.add_handler(CommandHandler('start', start))
    app_bot.add_handler(verify_conv)
    app_bot.add_handler(CallbackQueryHandler(check_join_status, pattern='^check_join_status$'))
    app_bot.add_handler(CallbackQueryHandler(language_handler, pattern='^lang_'))
    app_bot.add_handler(CallbackQueryHandler(show_registration_info, pattern='^start_earning$'))
    app_bot.add_handler(CallbackQueryHandler(play_hack_menu, pattern='^play_hack_action$'))

    print("Bot is starting...")
    app_bot.run_polling()
