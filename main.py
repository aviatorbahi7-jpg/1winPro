import firebase_admin
from firebase_admin import credentials, firestore
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
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ================= FIREBASE SETUP (সম্পূর্ণ সঠিক কনফিগ) =================
firebase_config = {
  "type": "service_account",
  "project_id": "winbot-eea9a",
  "private_key_id": "0fc394504ed2eb8954ec426bbe11f46eec38ffb0",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDGPOJtItY6HTIS\nqr+K+wiVmjaa1hl+qpRlHH6AjdUHVEIoVteooVHleZW/XlJZRyNMnp0fnqcChb/9\n5uXbLreay1UEnmwFUmxoqGADbxh9FSrCoyczrIGXr3EfoENxH9wVU8dtwlK6g1fY\nl0e8btmweoTsDt8qCA1BfaOBKccWCFkkg2wu8zVqghTOCw09/upzgTPALvuwDcDC\nWNpYzj87y2j+f2CMdu4RRiDZ+VosIIhSAAV1Y193UELcZDTv5/Wlj6mbKWb+O0xK\n8Yp5Z3LS/Yg4T+IsDHCxmk+3Ul3qPNb8Avuy0HuWBEgwj4rqxBoMMTjUIopp1h69\nxzbFkKu7AgMBAAECggEAAXVeNxkBWXvF1rRR5McJs6Fm/cb4eLbu5jrfmrjbFIrj\n/QxShDJCT31lrXrsq9fQTyvVkm97jBMJgWfgULdXG3jxKa+0B2qpUzB18GCHXhg4\nmyZRz1lZZLvM3xjclimlWAoolp/44C1qM9+SZApZaKkmGYnXI3sxWcYqXJ9pkGRr\nrSPZw77hY3H+2ByNO6mBGYR+yecjvTOUcBZuIqgkEmv+dRhec/QllmXZCDTYyWWM\nj6iAA1ARAQ9tep5tsv4tDUI801v24SJ0ulQLDFvaEZ16fSBu0fTnjDYeK8ukSQYB\nNfUbfGQRLeeii8XCktPtP47Vda5x9kM3ANRJdJ7FmQKBgQDwLRqqKXgjumOmY78F\ndvP/p5iYaH1nsEJ6m/JxgzyHIwhu1xS7v7KRyjLZyxTD614FK15qh3nX0A/Q2+M5\nQywNhMXnPPB01tMsFJTFKVb7TBa9XcVtQcV7XPHugceKAFUp3nQC1sw1lKKluFWb\vuXKdkigHJ4EiNWERgoBfjyv6QKBgQDTTG7qDldWLs8UXVglwBpaMXGw/PEJxkiW\n8MHKCbhEfwU7PCB2yoB3mN+5tjPJ49g28J7FaklIwjBRxGFP3rVVtnJ2vyQzfr6n\nL1D6jAZUPLjmUWx8rCB2jWFL7eBxVlPc63tE33CMGpxq8oiBkyKsPf61pRLqNEP6\zzCJIKA8AwKBgQCPi1WRd+F+8QpXyuvDF1ozZPZ1uJWi4ByLbSMUpswJNG342QFi\nSOsv6TpFIvQROF3kFwyB/OBclNSvDoyaj8QHfGBPmQNZwX9KrC5SPCfpX4uDuESj\nzRh7Z4yM8PHST+qWcIbDn59DMseW5jn8MLbkL5euYgwrR6DdQoL+a3VX6QKBgQCC\nKe+Zl8QNf0Bp1ybZ+oFBVnwm/2qtDszgzudSQrKU33qlhuCozQ5ennoTuT4l/InR\nLmFgU51ZiOajOEqKHTOv3Xid1hnC7y0baHaGIYQ0mEN+/mHKW26UGXv6fktpBjkb\nOqTxRIPcivgYmdelmrIdUQN7enkwdYn7E29eyg5raQKBgG/kppUI/hJy0sA2TkWW\nIS/poxxHLw3VO2mNDJKhW+n1okzJ2x3Ftx3han2AlAUXmLXiOH+R0GKRpT7Xtz8J\nDP4rNxnZJ8smPuWIC4YbI9kEDrF4Pgd2USmawrycMqZdcTJ6jtSMHUdVJoTbgyd1\nicEVdXxDzM5IGdi42DcSyGBB\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@winbot-eea9a.iam.gserviceaccount.com",
  "client_id": "111122027484565922605",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40winbot-eea9a.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    logger.info("Firebase connected successfully!")
except Exception as e:
    logger.error(f"Firebase initial error: {e}")

# ================= FLASK SERVER =================
flask_app = Flask(__name__)
@flask_app.route('/')
def index(): return "BOT STATUS: ACTIVE"

def run_flask_server():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

# ================= CONFIGURATION =================
BOT_TOKEN = "8525057709:AAEXv7b8l8tA9qb1KuCDtlv74d9LtaVWe1Q"
ADMIN_ID = 1146186608
REQUIRED_CHANNEL = -1001481593780
CHANNEL_LINK = "https://t.me/+3U0nMzWs4Aw0YjFl"

# Images
IMAGE_WELCOME = "https://i.ibb.co/XfxnhBYY/file-000000006ac47206b9a3e5b41d2e17e1.png"
IMAGE_REG = "https://i.ibb.co/PZ5VTZVT/IMG-20260201-052425-386.jpg"
IMAGE_SUCCESS = "https://i.ibb.co/fdwt2s8D/file-00000000973471faba7ce65cd5c96718.png"

# Game Links
LINK_AVIATOR = "https://aviatorgameadmin.netlify.app/"
LINK_MINES = "https://mines-game-hack.netlify.app/"

# States
WAITING_FOR_ID = 1

LANGUAGES = {
    'en': {'name': '🇺🇸 English', 'earn_btn': 'Start Earning', 'reg_btn': 'Registration', 'verify_btn': '✅ Verify ID', 'ask_id': 'Send 9-digit ID:', 'success': '✅ VERIFIED!'},
    'bd': {'name': '🇧🇩 Bangla', 'earn_btn': 'টাকা আয় শুরু করুন', 'reg_btn': 'রেজিস্ট্রেশন', 'verify_btn': '✅ ভেরিফাই করুন', 'ask_id': 'আপনার ৯ ডিজিট আইডি দিন:', 'success': '✅ ভেরিফাইড!'},
}

# ================= UTILS =================
def save_user(user_id):
    try:
        db.collection('users').document(str(user_id)).set({'id': user_id}, merge=True)
    except Exception as e:
        logger.error(f"Save user error: {e}")

async def check_membership(user_id, context):
    try:
        member = await context.bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)
    
    if await check_membership(user_id, context):
        keyboard = [[InlineKeyboardButton("English", callback_data='l_en'), InlineKeyboardButton("Bangla", callback_data='l_bd')]]
        await update.message.reply_text("<b>Welcome! Select Language:</b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    else:
        btn = [[InlineKeyboardButton("Join Channel", url=CHANNEL_LINK)], [InlineKeyboardButton("Verify Joined", callback_data='recheck')]]
        await update.message.reply_text("❌ Join our channel first to use this bot!", reply_markup=InlineKeyboardMarkup(btn))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data.startswith('l_'):
        lang = data.split('_')[1]
        context.user_data['lang'] = lang
        btn = [[InlineKeyboardButton(LANGUAGES[lang]['earn_btn'], callback_data='step_reg')]]
        await query.message.delete()
        await context.bot.send_photo(query.from_user.id, IMAGE_WELCOME, caption="Welcome! Let's start earning.", reply_markup=InlineKeyboardMarkup(btn))

    elif data == 'step_reg':
        lang = context.user_data.get('lang', 'en')
        btn = [[InlineKeyboardButton(LANGUAGES[lang]['reg_btn'], url="https://1wezue.com/casino")],
               [InlineKeyboardButton(LANGUAGES[lang]['verify_btn'], callback_data='ask_id')]]
        await query.message.delete()
        await context.bot.send_photo(query.from_user.id, IMAGE_REG, caption="<b>Step 1: Register Account</b>\n\nPromo Code: <b>BLACK110</b>", parse_mode='HTML', reply_markup=InlineKeyboardMarkup(btn))

    elif data == 'ask_id':
        lang = context.user_data.get('lang', 'en')
        await query.message.reply_text(LANGUAGES[lang]['ask_id'])
        context.user_data['state'] = WAITING_FOR_ID

    elif data == 'hack_menu':
        btn = [[InlineKeyboardButton("✈️ Aviator Hack", web_app=WebAppInfo(url=LINK_AVIATOR))],
               [InlineKeyboardButton("💣 Mines Hack", web_app=WebAppInfo(url=LINK_MINES))]]
        await query.message.reply_text("🎮 <b>Select Game:</b>", reply_markup=InlineKeyboardMarkup(btn), parse_mode='HTML')

    elif data == 'recheck':
        if await check_membership(query.from_user.id, context):
            await query.message.edit_text("✅ Membership verified! Type /start to begin.")
        else:
            await query.answer("❌ You haven't joined yet!", show_alert=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('state') == WAITING_FOR_ID:
        lang = context.user_data.get('lang', 'en')
        msg = await update.message.reply_text("🔄 Analyzing your ID...")
        await asyncio.sleep(2)
        await msg.delete()
        btn = [[InlineKeyboardButton("🎮 Open Hack Menu", callback_data='hack_menu')]]
        await update.message.reply_photo(IMAGE_SUCCESS, caption=LANGUAGES[lang]['success'], reply_markup=InlineKeyboardMarkup(btn))
        context.user_data['state'] = None

# ================= MAIN RUNNER =================
if __name__ == '__main__':
    # Flask সার্ভার থ্রেড
    Thread(target=run_flask_server, daemon=True).start()
    
    # বট অ্যাপ্লিকেশন
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot is starting...")
    app.run_polling(drop_pending_updates=True)
