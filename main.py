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
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= FIREBASE SETUP =================
# আপনার দেওয়া সার্ভিস অ্যাকাউন্ট কি
firebase_config = {
  "type": "service_account",
  "project_id": "winbot-eea9a",
  "private_key_id": "0fc394504ed2eb8954ec426bbe11f46eec38ffb0",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDGPOJtItY6HTIS\nqr+K+wiVmjaa1hl+qpRlHH6AjdUHVEIoVteooVHleZW/XlJZRyNMnp0fnqcChb/9\n5uXbLreay1UEnmwFUmxoqGADbxh9FSrCoyczrIGXr3EfoENxH9wVU8dtwlK6g1fY\nl0e8btmweoTsDt8qCA1BfaOBKccWCFkkg2wu8zVqghTOCw09/upzgTPALvuwDcDC\nWNpYzj87y2j+f2CMdu4RRiDZ+VosIIhSAAV1Y193UELcZDTv5/Wlj6mbKWb+O0xK\n8Yp5Z3LS/Yg4T+IsDHCxmk+3Ul3qPNb8Avuy0HuWBEgwj4rqxBoMMTjUIopp1h69\nxzbFkKu7AgMBAAECggEAAXVeNxkBWXvF1rRR5McJs6Fm/cb4eLbu5jrfmrjbFIrj\n/QxShDJCT31lrXrsq9fQTyvVkm97jBMJgWfgULdXG3jxKa+0B2qpUzB18GCHXhg4\nmyZRz1lZZLvM3xjclimlWAoolp/44C1qM9+SZApZaKkmGYnXI3sxWcYqXJ9pkGRr\nrSPZw77hY3H+2ByNO6mBGYR+yecjvTOUcBZuIqgkEmv+dRhec/QllmXZCDTYyWWM\nj6iAA1ARAQ9tep5tsv4tDUI801v24SJ0ulQLDFvaEZ16fSBu0fTnjDYeK8ukSQYB\nNfUbfGQRLeeii8XCktPtP47Vda5x9kM3ANRJdJ7FmQKBgQDwLRqqKXgjumOmY78F\ndvP/p5iYaH1nsEJ6m/JxgzyHIwhu1xS7v7KRyjLZyxTD614FK15qh3nX0A/Q2+M5\QywNhMXnPPB01tMsFJTFKVb7TBa9XcVtQcV7XPHugceKAFUp3nQC1sw1lKKluFWb\vuXKdkigHJ4EiNWERgoBfjyv6QKBgQDTTG7qDldWLs8UXVglwBpaMXGw/PEJxkiW\n8MHKCbhEfwU7PCB2yoB3mN+5tjPJ49g28J7FaklIwjBRxGFP3rVVtnJ2vyQzfr6n\nL1D6jAZUPLjmUWx8rCB2jWFL7eBxVlPc63tE33CMGpxq8oiBkyKsPf61pRLqNEP6\zzCJIKA8AwKBgQCPi1WRd+F+8QpXyuvDF1ozZPZ1uJWi4ByLbSMUpswJNG342QFi\nSOsv6TpFIvQROF3kFwyB/OBclNSvDoyaj8QHfGBPmQNZwX9KrC5SPCfpX4uDuESj\nzRh7Z4yM8PHST+qWcIbDn59DMseW5jn8MLbkL5euYgwrR6DdQoL+a3VX6QKBgQCC\nKe+Zl8QNf0Bp1ybZ+oFBVnwm/2qtDszgzudSQrKU33qlhuCozQ5ennoTuT4l/InR\nLmFgU51ZiOajOEqKHTOv3Xid1hnC7y0baHaGIYQ0mEN+/mHKW26UGXv6fktpBjkb\nOqTxRIPcivgYmdelmrIdUQN7enkwdYn7E29eyg5raQKBgG/kppUI/hJy0sA2TkWW\nIS/poxxHLw3VO2mNDJKhW+n1okzJ2x3Ftx3han2AlAUXmLXiOH+R0GKRpT7Xtz8J\nDP4rNxnZJ8smPuWIC4YbI9kEDrF4Pgd2USmawrycMqZdcTJ6jtSMHUdVJoTbgyd1\nicEVdXxDzM5IGdi42DcSyGBB\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@winbot-eea9a.iam.gserviceaccount.com",
  "client_id": "111122027484565922605",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40winbot-eea9a.iam.gserviceaccount.com",
}

if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ================= FLASK SERVER =================
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# ================= CONFIGURATION =================
BOT_TOKEN = "8525057709:AAEXv7b8l8tA9qb1KuCDtlv74d9LtaVWe1Q"
ADMIN_ID = 1146186608
REQUIRED_CHANNEL = -1001481593780
CHANNEL_LINK = "https://t.me/+3U0nMzWs4Aw0YjFl"

# Images Links (আপনার দেওয়া অরিজিনাল লিংক)
IMAGE_URL_WELCOME = "https://i.ibb.co/XfxnhBYY/file-000000006ac47206b9a3e5b41d2e17e1.png"
IMAGE_URL_REG = "https://i.ibb.co/PZ5VTZVT/IMG-20260201-052425-386.jpg"
IMAGE_URL_SUCCESS = "https://i.ibb.co/fdwt2s8D/file-00000000973471faba7ce65cd5c96718.png"
IMAGE_URL_HACK_MENU = "https://i.ibb.co/C3YqyxJn/Data-Breach-at-Betting-Platform-1win-Exposed-96-Million-Users.png"

# Game URLs
LINK_AVIATOR = "https://aviatorgameadmin.netlify.app/"
LINK_MINES = "https://mines-game-hack.netlify.app/"

# States
WAITING_FOR_ID, BROADCAST_SIMPLE, BTN_MSG, BTN_LABEL, BTN_URL = range(1, 6)

LANGUAGES = {
    'en': {'earn_btn': 'Start Earning', 'reg_btn': 'Registration', 'verify_btn': '✅ Verify ID', 'ask_id': 'Send 9-digit ID:', 'analyzing': '🔄 Analyzing...', 'success_msg': '✅ <b>VERIFIED!</b>', 'play_btn': '🎮 Play Hack', 'select_game': 'Select Game:'},
    'hi': {'earn_btn': 'पैसे कमाएं', 'reg_btn': 'पंजीकरण', 'verify_btn': '✅ सत्यापित करें', 'ask_id': 'अपनी ID भेजें:', 'analyzing': '🔄 जांच हो रही है...', 'success_msg': '✅ <b>सत्यापित!</b>', 'play_btn': '🎮 हैक के साथ खेलें', 'select_game': 'गेম चुनें:'},
    'bd': {'earn_btn': 'টাকা আয় শুরু করুন', 'reg_btn': 'রেজিস্ট্রেশন', 'verify_btn': '✅ ভেরিফাই করুন', 'ask_id': 'আপনার ৯ ডিজিট আইডি দিন:', 'analyzing': '🔄 যাচাই হচ্ছে...', 'success_msg': '✅ <b>ভেরিফাইড!</b>', 'play_btn': '🎮 হ্যাক দিয়ে খেলুন', 'select_game': 'গেম সিলেক্ট করুন:'},
}

# ================= UTILS =================
def save_user_to_db(user_id):
    db.collection('users').document(str(user_id)).set({'user_id': user_id}, merge=True)

def get_total_users():
    users = db.collection('users').stream()
    return [u.id for u in users]

async def check_membership(user_id, context):
    try:
        m = await context.bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return m.status in [ChatMember.MEMBER, ChatMember.OWNER, ChatMember.ADMINISTRATOR]
    except: return False

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user_to_db(user_id)
    
    if await check_membership(user_id, context):
        keyboard = [[InlineKeyboardButton("🇺🇸 English", callback_data='lang_en'), InlineKeyboardButton("🇮🇳 Hindi", callback_data='lang_hi')],
                    [InlineKeyboardButton("🇧🇩 Bangla", callback_data='lang_bd')]]
        await update.message.reply_text("<b>Welcome! Select your language:</b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    else:
        btn = [[InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)], [InlineKeyboardButton("✅ Joined / Verify", callback_data='check_join')]]
        await update.message.reply_text("⚠️ <b>Join our private channel first!</b>", reply_markup=InlineKeyboardMarkup(btn), parse_mode='HTML')

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await check_membership(query.from_user.id, context):
        await query.answer("Access Granted!")
        keyboard = [[InlineKeyboardButton("🇺🇸 English", callback_data='lang_en'), InlineKeyboardButton("🇮🇳 Hindi", callback_data='lang_hi')],
                    [InlineKeyboardButton("🇧🇩 Bangla", callback_data='lang_bd')]]
        await query.message.edit_text("<b>Welcome! Select your language:</b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    else:
        await query.answer("❌ You haven't joined yet!", show_alert=True)

async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = query.data.split('_')[1]
    context.user_data['lang'] = lang
    btn = [[InlineKeyboardButton(LANGUAGES[lang]['earn_btn'], callback_data='start_reg')]]
    await query.message.delete()
    await context.bot.send_photo(update.effective_chat.id, IMAGE_URL_WELCOME, caption="<b>Language Selected!</b>\nClick below to start.", reply_markup=InlineKeyboardMarkup(btn), parse_mode='HTML')

async def start_reg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'en')
    btn = [[InlineKeyboardButton(LANGUAGES[lang]['reg_btn'], url="https://1wezue.com/casino")],
           [InlineKeyboardButton(LANGUAGES[lang]['verify_btn'], callback_data='verify_step')]]
    await update.callback_query.message.delete()
    await context.bot.send_photo(update.effective_chat.id, IMAGE_URL_REG, caption="<b>Step 1: Register Account</b>\n\nPromo Code: <b>BLACK110</b>", parse_mode='HTML', reply_markup=InlineKeyboardMarkup(btn))

async def verify_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'en')
    await update.callback_query.message.reply_text(LANGUAGES[lang]['ask_id'])
    return WAITING_FOR_ID

async def receive_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'en')
    msg = await update.message.reply_text(LANGUAGES[lang]['analyzing'])
    await asyncio.sleep(2)
    await msg.delete()
    btn = [[InlineKeyboardButton(LANGUAGES[lang]['play_btn'], callback_data='hack_menu')]]
    await update.message.reply_photo(IMAGE_URL_SUCCESS, caption=LANGUAGES[lang]['success_msg'], parse_mode='HTML', reply_markup=InlineKeyboardMarkup(btn))
    return ConversationHandler.END

async def hack_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'en')
    btn = [
        [InlineKeyboardButton("✈️ Aviator Hack", web_app=WebAppInfo(url=LINK_AVIATOR))],
        [InlineKeyboardButton("💣 Mines Hack", web_app=WebAppInfo(url=LINK_MINES))],
        [InlineKeyboardButton("🔙 Back", callback_data='start_reg')]
    ]
    if update.callback_query:
        await update.callback_query.message.delete()
    await context.bot.send_photo(update.effective_chat.id, IMAGE_URL_HACK_MENU, caption=LANGUAGES[lang]['select_game'], reply_markup=InlineKeyboardMarkup(btn))

# ================= ADMIN PANEL =================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    users = get_total_users()
    btn = [
        [InlineKeyboardButton("📝 Simple Broadcast", callback_data='admin_bc_simple')],
        [InlineKeyboardButton("🔗 Button Broadcast", callback_data='admin_bc_btn')],
        [InlineKeyboardButton("❌ Close", callback_data='admin_close')]
    ]
    await update.message.reply_text(f"👑 <b>Admin Panel</b>\nTotal Users: {len(users)}", reply_markup=InlineKeyboardMarkup(btn), parse_mode='HTML')

async def bc_simple_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text("Send the message (Text/Photo/Video) for Broadcast. /cancel to stop.")
    return BROADCAST_SIMPLE

async def bc_simple_run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = get_total_users()
    count = 0
    for u in users:
        try:
            await context.bot.copy_message(chat_id=u, from_chat_id=update.effective_chat.id, message_id=update.message.message_id)
            count += 1
            await asyncio.sleep(0.05)
        except: continue
    await update.message.reply_text(f"✅ Sent to {count} users.")
    return ConversationHandler.END

async def bc_btn_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text("Step 1: Send the Broadcast Content.")
    return BTN_MSG

async def bc_btn_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['bc_msg_id'] = update.message.message_id
    await update.message.reply_text("Step 2: Send Button Name.")
    return BTN_LABEL

async def bc_btn_label(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['bc_label'] = update.message.text
    await update.message.reply_text("Step 3: Send Button URL.")
    return BTN_URL

async def bc_btn_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    label = context.user_data['bc_label']
    msg_id = context.user_data['bc_msg_id']
    btn = [[InlineKeyboardButton(label, url=url)]]
    users = get_total_users()
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
    await update.message.reply_text("Process Cancelled.")
    return ConversationHandler.END

# ================= MAIN RUNNER =================
if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()
    
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # ID Verification Conversation
    id_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(verify_step, pattern='^verify_step$')],
        states={WAITING_FOR_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_id)]},
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # Admin Broadcast Conversation
    admin_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(bc_simple_start, pattern='^admin_bc_simple$'),
            CallbackQueryHandler(bc_btn_start, pattern='^admin_bc_btn$')
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
    application.add_handler(CommandHandler('admin', admin_panel))
    application.add_handler(id_conv)
    application.add_handler(admin_conv)
    application.add_handler(CallbackQueryHandler(check_join, pattern='^check_join$'))
    application.add_handler(CallbackQueryHandler(language_handler, pattern='^lang_'))
    application.add_handler(CallbackQueryHandler(start_reg, pattern='^start_reg$'))
    application.add_handler(CallbackQueryHandler(hack_menu, pattern='^hack_menu$'))
    application.add_handler(CallbackQueryHandler(lambda u,c: u.callback_query.message.delete(), pattern='^admin_close$'))

    print("Bot is LIVE with Images, Admin Panel & Firebase...")
    application.run_polling(drop_pending_updates=True)
