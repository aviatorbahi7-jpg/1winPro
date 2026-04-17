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
from telegram.error import BadRequest, Forbidden, RetryAfter

# ================= LOGGING =================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================= FLASK SERVER (For Render) =================
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    try:
        port = int(os.environ.get('PORT', 8080))
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Flask Error: {e}")

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ================= CONFIGURATION =================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8525057709:AAEXv7b8l8tA9qb1KuCDtlv74d9LtaVWe1Q")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1146186608"))
REQUIRED_CHANNEL = int(os.getenv("REQUIRED_CHANNEL", "-1001481593780"))
CHANNEL_LINK = "https://t.me/+3U0nMzWs4Aw0YjFl"

# Media Links
IMAGE_URL_WELCOME = "https://i.ibb.co/XfxnhBYY/file-000000006ac47206b9a3e5b41d2e17e1.png"
IMAGE_URL_REG = "https://i.ibb.co/PZ5VTZVT/IMG-20260201-052425-386.jpg"
IMAGE_URL_SUCCESS = "https://i.ibb.co/fdwt2s8D/file-00000000973471faba7ce65cd5c96718.png"
IMAGE_URL_HACK_MENU = "https://i.ibb.co/C3YqyxJn/Data-Breach-at-Betting-Platform-1win-Exposed-96-Million-Users.png"

# Game URLs
LINK_AVIATOR = "https://aviatorbahohacker.fwh.is/"
LINK_MINES = "https://mines-game-hack.netlify.app/"

USER_FILE = "users.txt"

# States
WAITING_FOR_ID = 1
BROADCAST_SIMPLE = 2

# Languages
LANGUAGES = {
    'en': {
        'name': '🇺🇸 English', 
        'earn_btn': 'Start Earning Money', 
        'reg_btn': 'Registration Link', 
        'verify_btn': '✅ I have Registered (Verify)', 
        'ask_id': 'Please send your 9-digit Account ID:', 
        'analyzing': '🔄 Verifying your ID...', 
        'success_msg': '✅ <b>ACCOUNT VERIFIED!</b>\n\nYour account has been successfully synchronized.', 
        'play_btn': '🎮 Play With Hack',
        'select_game': 'Select a game to start hacking:'
    },
    'hi': {
        'name': '🇮🇳 India (Hindi)', 
        'earn_btn': 'पैसे कमाना शुरू करें', 
        'reg_btn': 'पंजीकरण (Registration)', 
        'verify_btn': '✅ मैंने पंजीकरण किया है (Verify)', 
        'ask_id': 'कृपया अपनी 9-অंकीय खाता आईडी भेजें:', 
        'analyzing': '🔄 खाता जाँचा जा रहा है...', 
        'success_msg': '✅ <b>खाता सत्यापित!</b>', 
        'play_btn': '🎮 Play With Hack',
        'select_game': 'गेম चुनें:'
    },
    'bd': {
        'name': '🇧🇩 Bangladesh (Bangla)', 
        'earn_btn': 'টাকা আয় শুরু করুন', 
        'reg_btn': 'রেজিস্ট্রেশন লিংক', 
        'verify_btn': '✅ আমার রেজিস্ট্রেশন সম্পন্ন হয়েছে', 
        'ask_id': 'অনুগ্রহ করে আপনার ৯ ডিজিটের একাউন্ট আইডি দিন:', 
        'analyzing': '🔄 আপনার আইডি যাচাই করা হচ্ছে...', 
        'success_msg': '✅ <b>একাউন্ট ভেরিফাইড!</b>\n\nআপনার একাউন্টটি সফলভাবে বটের সাথে যুক্ত হয়েছে।', 
        'play_btn': '🎮 হ্যাক দিয়ে খেলুন',
        'select_game': 'হ্যাক শুরু করতে একটি গেম সিলেক্ট করুন:'
    },
}

# ================= UTILS =================
def save_user(user_id):
    if not os.path.exists(USER_FILE):
        open(USER_FILE, "w").close()
    with open(USER_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USER_FILE, "a") as f:
            f.write(f"{user_id}\n")

def get_users():
    if not os.path.exists(USER_FILE): return []
    with open(USER_FILE, "r") as f:
        return f.read().splitlines()

async def check_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return member.status in [ChatMember.MEMBER, ChatMember.OWNER, ChatMember.ADMINISTRATOR]
    except: return False

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)
    
    if await check_membership(user_id, context):
        return await send_language_menu(update, context)
    
    keyboard = [[InlineKeyboardButton("📢 Join Private Channel", url=CHANNEL_LINK)],
                [InlineKeyboardButton("✅ Joined / Verify", callback_data='check_join_status')]]
    await update.message.reply_text("⚠️ <b>Join Channel First!</b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

async def check_join_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await check_membership(query.from_user.id, context):
        await query.answer("Success!")
        await send_language_menu(update, context)
    else:
        await query.answer("❌ You haven't joined yet!", show_alert=True)

async def send_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(v['name'], callback_data=f'lang_{k}') for k, v in list(LANGUAGES.items())[:2]],
                [InlineKeyboardButton(LANGUAGES['bd']['name'], callback_data='lang_bd')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = "Hello! Please select your language:"
    if update.callback_query:
        await update.callback_query.message.edit_text(msg, reply_markup=reply_markup)
    else:
        await update.message.reply_text(msg, reply_markup=reply_markup)

async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang_code = query.data.split('_')[1]
    context.user_data['selected_lang'] = lang_code
    lang_data = LANGUAGES.get(lang_code, LANGUAGES['en'])
    keyboard = [[InlineKeyboardButton(lang_data['earn_btn'], callback_data='start_earning')]]
    await query.message.delete()
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=IMAGE_URL_WELCOME, caption=f"Language: {lang_data['name']}", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_registration_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang_code = context.user_data.get('selected_lang', 'en')
    lang_data = LANGUAGES.get(lang_code, LANGUAGES['en'])
    info_text = "<b>Step 1 - Register.</b>\nUse Promo: <b>BLACK110</b>"
    keyboard = [[InlineKeyboardButton(lang_data['reg_btn'], url="https://1wezue.com/casino")],
                [InlineKeyboardButton(lang_data['verify_btn'], callback_data='verify_reg')]]
    await update.callback_query.message.delete()
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=IMAGE_URL_REG, caption=info_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def verify_process_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    lang_code = context.user_data.get('selected_lang', 'en')
    await update.effective_chat.send_message(LANGUAGES[lang_code]['ask_id'])
    return WAITING_FOR_ID

async def receive_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    lang_code = context.user_data.get('selected_lang', 'en')
    
    if not user_input.isdigit() or len(user_input) < 7:
        await update.message.reply_text("❌ Invalid ID! Send a valid 9-digit Account ID.")
        return WAITING_FOR_ID

    msg = await update.message.reply_text(LANGUAGES[lang_code]['analyzing'])
    await asyncio.sleep(2)
    await msg.delete()
    
    keyboard = [[InlineKeyboardButton(LANGUAGES[lang_code]['play_btn'], callback_data='play_hack_action')]]
    await update.message.reply_photo(photo=IMAGE_URL_SUCCESS, caption=LANGUAGES[lang_code]['success_msg'], parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
    return ConversationHandler.END

async def play_hack_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang_code = context.user_data.get('selected_lang', 'en')
    keyboard = [[InlineKeyboardButton("✈️ Aviator", url=LINK_AVIATOR)],
                [InlineKeyboardButton("💣 Mines", url=LINK_MINES)],
                [InlineKeyboardButton("🔙 Back", callback_data='start_earning')]]
    await update.callback_query.message.delete()
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=IMAGE_URL_HACK_MENU, caption=LANGUAGES[lang_code]['select_game'], reply_markup=InlineKeyboardMarkup(keyboard))

# ================= ADMIN PANEL =================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    users = get_users()
    keyboard = [[InlineKeyboardButton("📝 Broadcast Message", callback_data='admin_simple')],
                [InlineKeyboardButton("❌ Close", callback_data='admin_close')]]
    await update.message.reply_text(f"👑 Admin Panel\nTotal Users: {len(users)}", reply_markup=InlineKeyboardMarkup(keyboard))

async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text("Send broadcast message (Text or Photo with Caption). /cancel to stop.")
    return BROADCAST_SIMPLE

async def perform_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = get_users()
    count = 0
    for uid in users:
        try:
            if update.message.photo:
                await context.bot.send_photo(chat_id=int(uid), photo=update.message.photo[-1].file_id, caption=update.message.caption)
            else:
                await context.bot.send_message(chat_id=int(uid), text=update.message.text)
            count += 1
            await asyncio.sleep(0.05)
        except Exception: continue
    
    await update.message.reply_text(f"✅ Sent to {count} users.")
    return ConversationHandler.END

# ================= MAIN =================
if __name__ == '__main__':
    # ১. ফ্লাস্ক সার্ভার চালু
    keep_alive()
    
    # ২. বট অ্যাপ সেটআপ
    try:
        app_bot = ApplicationBuilder().token(BOT_TOKEN).build()

        # কনভারসেশন হ্যান্ডলারসমূহ
        verify_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(verify_process_start, pattern='^verify_reg$')],
            states={WAITING_FOR_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_id)]},
            fallbacks=[CommandHandler('cancel', lambda u,c: ConversationHandler.END)]
        )

        admin_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(start_broadcast, pattern='^admin_simple$')],
            states={BROADCAST_SIMPLE: [MessageHandler(filters.ALL & ~filters.COMMAND, perform_broadcast)]},
            fallbacks=[CommandHandler('cancel', lambda u,c: ConversationHandler.END)]
        )

        # হ্যান্ডলার অ্যাড করা
        app_bot.add_handler(CommandHandler('start', start))
        app_bot.add_handler(CommandHandler('admin', admin_panel))
        app_bot.add_handler(verify_conv)
        app_bot.add_handler(admin_conv)
        app_bot.add_handler(CallbackQueryHandler(check_join_status, pattern='^check_join_status$'))
        app_bot.add_handler(CallbackQueryHandler(language_handler, pattern='^lang_'))
        app_bot.add_handler(CallbackQueryHandler(show_registration_info, pattern='^start_earning$'))
        app_bot.add_handler(CallbackQueryHandler(play_hack_menu, pattern='^play_hack_action$'))
        app_bot.add_handler(CallbackQueryHandler(lambda u,c: u.callback_query.message.delete(), pattern='^admin_close$'))

        print("Bot is running...")
        app_bot.run_polling()
        
    except Exception as e:
        logger.error(f"Critical Error: {e}")
