import logging
import asyncio
import os
import sys
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember, WebAppInfo
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters, 
    ConversationHandler
)

# লগিং সেটআপ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= FLASK SERVER (Render Keep-Alive) =================
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive and Running!"

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

# Images Links
IMAGE_URL_WELCOME = "https://i.ibb.co/XfxnhBYY/file-000000006ac47206b9a3e5b41d2e17e1.png"
IMAGE_URL_REG = "https://i.ibb.co/PZ5VTZVT/IMG-20260201-052425-386.jpg"
IMAGE_URL_SUCCESS = "https://i.ibb.co/fdwt2s8D/file-00000000973471faba7ce65cd5c96718.png"
IMAGE_URL_HACK_MENU = "https://i.ibb.co/C3YqyxJn/Data-Breach-at-Betting-Platform-1win-Exposed-96-Million-Users.png"

# Game Hack URLs (Web App এর মাধ্যমে ওপেন হবে)
LINK_AVIATOR = "https://aviatorbahohacker.fwh.is/"
LINK_MINES = "https://mines-game-hack.netlify.app/"

USER_FILE = "users.txt"

# States for Conversations
WAITING_FOR_ID = 1
BROADCAST_SIMPLE = 2
BTN_MSG = 3
BTN_LABEL = 4
BTN_URL = 5

LANGUAGES = {
    'en': {'name': '🇺🇸 English', 'earn_btn': 'Start Earning', 'reg_btn': 'Registration', 'verify_btn': '✅ Verify ID', 'ask_id': 'Send 9-digit ID:', 'analyzing': '🔄 Analyzing...', 'success_msg': '✅ <b>VERIFIED!</b>', 'play_btn': '🎮 Play Hack', 'select_game': 'Select Game:'},
    'hi': {'name': '🇮🇳 Hindi', 'earn_btn': 'पैसे कमाएं', 'reg_btn': 'पंजीकरण', 'verify_btn': '✅ सत्यापित करें', 'ask_id': 'अपनी আইডি भेजें:', 'analyzing': '🔄 जांच हो रही है...', 'success_msg': '✅ <b>सत्यापित!</b>', 'play_btn': '🎮 हैक के साथ खेलें', 'select_game': 'गेम चुनें:'},
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
        await update.message.reply_text("<b>Welcome! Select your language:</b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    else:
        btn = [[InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)], [InlineKeyboardButton("✅ Joined / Verify", callback_data='check_join')]]
        await update.message.reply_text("⚠️ <b>Join our private channel first!</b>", reply_markup=InlineKeyboardMarkup(btn), parse_mode='HTML')

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await check_membership(query.from_user.id, context):
        await query.answer("Access Granted!")
        # Re-trigger start logic
        user_id = query.from_user.id
        keyboard = [[InlineKeyboardButton(v['name'], callback_data=f'lang_{k}') for k, v in list(LANGUAGES.items())[:2]],
                    [InlineKeyboardButton(LANGUAGES['bd']['name'], callback_data='lang_bd')]]
        await query.message.edit_text("<b>Welcome! Select your language:</b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    else:
        await query.answer("❌ You haven't joined yet!", show_alert=True)

async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = query.data.split('_')[1]
    context.user_data['lang'] = lang
    btn = [[InlineKeyboardButton(LANGUAGES[lang]['earn_btn'], callback_data='start_reg')]]
    await query.message.delete()
    await context.bot.send_photo(update.effective_chat.id, IMAGE_URL_WELCOME, caption=f"Language: {LANGUAGES[lang]['name']}\n\nClick the button to continue.", reply_markup=InlineKeyboardMarkup(btn))

async def start_reg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'en')
    btn = [[InlineKeyboardButton(LANGUAGES[lang]['reg_btn'], url="https://1wezue.com/casino")],
           [InlineKeyboardButton(LANGUAGES[lang]['verify_btn'], callback_data='verify')]]
    await update.callback_query.message.delete()
    await context.bot.send_photo(update.effective_chat.id, IMAGE_URL_REG, caption="<b>Step 1: Register Account</b>\n\nPromo Code: <b>BLACK110</b>", parse_mode='HTML', reply_markup=InlineKeyboardMarkup(btn))

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
    # এখানে WebAppInfo ব্যবহার করা হয়েছে যাতে লিঙ্কের বদলে অ্যাপের মতো ওপেন হয়
    btn = [
        [InlineKeyboardButton("✈️ Aviator Hack", web_app=WebAppInfo(url=LINK_AVIATOR))],
        [InlineKeyboardButton("💣 Mines Hack", web_app=WebAppInfo(url=LINK_MINES))],
        [InlineKeyboardButton("🔙 Back", callback_data='start_reg')]
    ]
    await update.callback_query.message.delete()
    await context.bot.send_photo(update.effective_chat.id, IMAGE_URL_HACK_MENU, caption=LANGUAGES[lang]['select_game'], reply_markup=InlineKeyboardMarkup(btn))

# ================= ADMIN PANEL FEATURES =================
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    with open(USER_FILE, "r") as f: total = len(f.read().splitlines())
    btn = [
        [InlineKeyboardButton("📝 Simple Broadcast", callback_data='bc_simple')],
        [InlineKeyboardButton("🔗 Button Broadcast", callback_data='bc_btn')],
        [InlineKeyboardButton("❌ Close Panel", callback_data='admin_close')]
    ]
    await update.message.reply_text(f"👑 <b>Admin Panel</b>\n\nTotal Users: <code>{total}</code>", reply_markup=InlineKeyboardMarkup(btn), parse_mode='HTML')

# Simple Broadcast (Text/Photo/Video)
async def bc_simple_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text("Send me the broadcast message (Text/Photo). Type /cancel to exit.")
    return BROADCAST_SIMPLE

async def bc_simple_run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(USER_FILE, "r") as f: users = f.read().splitlines()
    count = 0
    for u in users:
        try:
            await context.bot.copy_message(chat_id=u, from_chat_id=update.effective_chat.id, message_id=update.message.message_id)
            count += 1
            await asyncio.sleep(0.05)
        except: continue
    await update.message.reply_text(f"✅ Sent to {count} users.")
    return ConversationHandler.END

# Button Broadcast (Custom Message + Custom Button)
async def bc_btn_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text("Step 1: Send the Message Content (Text/Photo).")
    return BTN_MSG

async def bc_btn_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['bc_msg_id'] = update.message.message_id
    await update.message.reply_text("Step 2: Send Button Name (e.g., 'Join Group')")
    return BTN_LABEL

async def bc_btn_label(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['bc_label'] = update.message.text
    await update.message.reply_text("Step 3: Send Button URL (Link)")
    return BTN_URL

async def bc_btn_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    label = context.user_data['bc_label']
    msg_id = context.user_data['bc_msg_id']
    btn = [[InlineKeyboardButton(label, url=url)]]
    
    with open(USER_FILE, "r") as f: users = f.read().splitlines()
    count = 0
    for u in users:
        try:
            await context.bot.copy_message(chat_id=u, from_chat_id=update.effective_chat.id, message_id=msg_id, reply_markup=InlineKeyboardMarkup(btn))
            count += 1
            await asyncio.sleep(0.05)
        except: continue
    await update.message.reply_text(f"✅ Button Broadcast Sent to {count} users.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END

# ================= MAIN RUNNER =================
if __name__ == '__main__':
    keep_alive() # Render keeps active
    try:
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # Verify ID Conv
        v_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(verify_start, pattern='^verify$')],
            states={WAITING_FOR_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_id)]},
            fallbacks=[CommandHandler('cancel', cancel)]
        )
        
        # Admin Broadcast Conv
        a_conv = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(bc_simple_start, pattern='^bc_simple$'),
                CallbackQueryHandler(bc_btn_start, pattern='^bc_btn$')
            ],
            states={
                BROADCAST_SIMPLE: [MessageHandler(filters.ALL & ~filters.COMMAND, bc_simple_run)],
                BTN_MSG: [MessageHandler(filters.ALL & ~filters.COMMAND, bc_btn_msg)],
                BTN_LABEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, bc_btn_label)],
                BTN_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, bc_btn_url)],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
        
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('admin', admin))
        application.add_handler(v_conv)
        application.add_handler(a_conv)
        application.add_handler(CallbackQueryHandler(check_join, pattern='^check_join$'))
        application.add_handler(CallbackQueryHandler(language_handler, pattern='^lang_'))
        application.add_handler(CallbackQueryHandler(start_reg, pattern='^start_reg$'))
        application.add_handler(CallbackQueryHandler(hack_menu, pattern='^hack_menu$'))
        application.add_handler(CallbackQueryHandler(lambda u,c: u.callback_query.message.delete(), pattern='^admin_close$'))

        print("Bot is working now...")
        application.run_polling()
    except Exception as e:
        print(f"FATAL ERROR: {e}")
