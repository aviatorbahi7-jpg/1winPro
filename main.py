import logging
import asyncio
import os
import sys
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

# লগিং
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= FLASK SERVER =================
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ================= CONFIGURATION =================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8525057709:AAEXv7b8l8tA9qb1KuCDtlv74d9LtaVWe1Q")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1146186608"))
REQUIRED_CHANNEL = int(os.getenv("REQUIRED_CHANNEL", "-1001481593780"))
CHANNEL_LINK = "https://t.me/+3U0nMzWs4Aw0YjFl"

# Images
IMAGE_URL_WELCOME = "https://i.ibb.co/XfxnhBYY/file-000000006ac47206b9a3e5b41d2e17e1.png"
IMAGE_URL_REG = "https://i.ibb.co/PZ5VTZVT/IMG-20260201-052425-386.jpg"
IMAGE_URL_SUCCESS = "https://i.ibb.co/fdwt2s8D/file-00000000973471faba7ce65cd5c96718.png"
IMAGE_URL_HACK_MENU = "https://i.ibb.co/C3YqyxJn/Data-Breach-at-Betting-Platform-1win-Exposed-96-Million-Users.png"

# Game Hacks
LINK_AVIATOR = "https://aviatorbahohacker.fwh.is/"
LINK_MINES = "https://mines-game-hack.netlify.app/"

USER_FILE = "users.txt"
WAITING_FOR_ID, BROADCAST_STATE = 1, 2

LANGUAGES = {
    'en': {'name': '🇺🇸 English', 'earn_btn': 'Start Earning', 'reg_btn': 'Registration', 'verify_btn': '✅ Verify ID', 'ask_id': 'Send 9-digit ID:', 'analyzing': '🔄 Analyzing...', 'success_msg': '✅ <b>VERIFIED!</b>', 'play_btn': '🎮 Play Hack', 'select_game': 'Select Game:'},
    'hi': {'name': '🇮🇳 Hindi', 'earn_btn': 'पैसे कमाएं', 'reg_btn': 'पंजीकरण', 'verify_btn': '✅ सत्यापित करें', 'ask_id': 'अपनी आईडी भेजें:', 'analyzing': '🔄 जांच हो रही है...', 'success_msg': '✅ <b>सत्यापित!</b>', 'play_btn': '🎮 हैक के साथ खेलें', 'select_game': 'गेम चुनें:'},
    'bd': {'name': '🇧🇩 Bangla', 'earn_btn': 'টাকা আয় শুরু করুন', 'reg_btn': 'রেজিস্ট্রেশন', 'verify_btn': '✅ ভেরিফাই করুন', 'ask_id': 'আপনার ৯ ডিজিট আইডি দিন:', 'analyzing': '🔄 যাচাই হচ্ছে...', 'success_msg': '✅ <b>ভেরিফাইড!</b>', 'play_btn': '🎮 হ্যাক দিয়ে খেলুন', 'select_game': 'গেম সিলেক্ট করুন:'},
}

# ================= UTILS =================
def save_user(user_id):
    if not os.path.exists(USER_FILE): open(USER_FILE, "w").close()
    with open(USER_FILE, "r") as f: users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USER_FILE, "a") as f: f.write(f"{user_id}\n")

async def check_membership(user_id, context):
    try:
        m = await context.bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return m.status in [ChatMember.MEMBER, ChatMember.OWNER, ChatMember.ADMINISTRATOR]
    except: return False

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)
    if await check_membership(user_id, context):
        keyboard = [[InlineKeyboardButton(v['name'], callback_data=f'lang_{k}') for k, v in list(LANGUAGES.items())[:2]],
                    [InlineKeyboardButton(LANGUAGES['bd']['name'], callback_data='lang_bd')]]
        await update.message.reply_text("Select Language:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        btn = [[InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)], [InlineKeyboardButton("✅ Joined", callback_data='check_join')]]
        await update.message.reply_text("⚠️ Join first!", reply_markup=InlineKeyboardMarkup(btn))

async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = query.data.split('_')[1]
    context.user_data['lang'] = lang
    btn = [[InlineKeyboardButton(LANGUAGES[lang]['earn_btn'], callback_data='start_reg')]]
    await query.message.delete()
    await context.bot.send_photo(update.effective_chat.id, IMAGE_URL_WELCOME, caption=f"Language: {LANGUAGES[lang]['name']}", reply_markup=InlineKeyboardMarkup(btn))

async def start_reg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'en')
    btn = [[InlineKeyboardButton(LANGUAGES[lang]['reg_btn'], url="https://1wezue.com/casino")],
           [InlineKeyboardButton(LANGUAGES[lang]['verify_btn'], callback_data='verify')]]
    await update.callback_query.message.delete()
    await context.bot.send_photo(update.effective_chat.id, IMAGE_URL_REG, caption="<b>Step 1: Register</b>", parse_mode='HTML', reply_markup=InlineKeyboardMarkup(btn))

async def verify_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'en')
    await update.callback_query.message.reply_text(LANGUAGES[lang]['ask_id'])
    return WAITING_FOR_ID

async def receive_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'en')
    m = await update.message.reply_text(LANGUAGES[lang]['analyzing'])
    await asyncio.sleep(2)
    await m.delete()
    btn = [[InlineKeyboardButton(LANGUAGES[lang]['play_btn'], callback_data='hack_menu')]]
    await update.message.reply_photo(IMAGE_URL_SUCCESS, caption=LANGUAGES[lang]['success_msg'], parse_mode='HTML', reply_markup=InlineKeyboardMarkup(btn))
    return ConversationHandler.END

async def hack_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'en')
    btn = [[InlineKeyboardButton("✈️ Aviator", url=LINK_AVIATOR)], [InlineKeyboardButton("💣 Mines", url=LINK_MINES)]]
    await update.callback_query.message.delete()
    await context.bot.send_photo(update.effective_chat.id, IMAGE_URL_HACK_MENU, caption=LANGUAGES[lang]['select_game'], reply_markup=InlineKeyboardMarkup(btn))

# ================= ADMIN =================
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    with open(USER_FILE, "r") as f: total = len(f.read().splitlines())
    btn = [[InlineKeyboardButton("📝 Broadcast", callback_data='bc')]]
    await update.message.reply_text(f"Admin Panel\nUsers: {total}", reply_markup=InlineKeyboardMarkup(btn))

async def bc_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("Send message to broadcast:")
    return BROADCAST_STATE

async def bc_run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(USER_FILE, "r") as f: users = f.read().splitlines()
    for u in users:
        try: await context.bot.copy_message(u, update.effective_chat.id, update.message.message_id)
        except: continue
    await update.message.reply_text("Broadcast Done!")
    return ConversationHandler.END

# ================= MAIN =================
if __name__ == '__main__':
    keep_alive()
    # build() এর সময় যাতে Python 3.14 ঝামেলা না করে, তাই try-except
    try:
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # Handlers
        v_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(verify_start, pattern='^verify$')],
            states={WAITING_FOR_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_id)]},
            fallbacks=[]
        )
        a_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(bc_start, pattern='^bc$')],
            states={BROADCAST_STATE: [MessageHandler(filters.ALL & ~filters.COMMAND, bc_run)]},
            fallbacks=[]
        )
        
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('admin', admin))
        application.add_handler(v_conv)
        application.add_handler(a_conv)
        application.add_handler(CallbackQueryHandler(language_handler, pattern='^lang_'))
        application.add_handler(CallbackQueryHandler(start_reg, pattern='^start_reg$'))
        application.add_handler(CallbackQueryHandler(hack_menu, pattern='^hack_menu$'))
        application.add_handler(CallbackQueryHandler(start, pattern='^check_join$'))

        print("Bot is starting...")
        application.run_polling()
    except Exception as e:
        print(f"FAILED: {e}")
