import logging
import asyncio
import os
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember, WebAppInfo
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ConversationHandler
)

# নতুন ফাইল থেকে ইম্পোর্ট
from verify_uid import mark_user_clicked, has_user_clicked, start_verification_animation

# লগিং সেটআপ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ================= FLASK SERVER =================
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ================= CONFIGURATION =================
BOT_TOKEN = "8525057709:AAEXv7b8l8tA9qb1KuCDtlv74d9LtaVWe1Q"
ADMIN_ID = 1146186608
REQUIRED_CHANNEL = -1001481593780
CHANNEL_LINK = "https://t.me/+3U0nMzWs4Aw0YjFl"
REG_LINK = "https://1wezue.com/casino"

# Images
IMAGE_URL_WELCOME = "https://i.ibb.co/XfxnhBYY/file-000000006ac47206b9a3e5b41d2e17e1.png"
IMAGE_URL_REG = "https://i.ibb.co/PZ5VTZVT/IMG-20260201-052425-386.jpg"
IMAGE_URL_SUCCESS = "https://i.ibb.co/fdwt2s8D/file-00000000973471faba7ce65cd5c96718.png"
IMAGE_URL_HACK_MENU = "https://i.ibb.co/C3YqyxJn/Data-Breach-at-Betting-Platform-1win-Exposed-96-Million-Users.png"

USER_FILE = "users.txt"
WAITING_FOR_ID = 1
BROADCAST_SIMPLE = 2

LANGUAGES = {
    'en': {
        'earn_btn': 'Start Earning', 'reg_btn': '1. Open Registration Link', 'verify_btn': '2. Verify My ID',
        'ask_id': '📩 Send your Player ID:', 
        'checking_steps': ['📡 Requesting Server...', '🔍 Checking Database...', '🔑 Verifying Promo BLACK110...'],
        'success': '✅ <b>ID VERIFIED!</b>', 
        'fail_no_click': '❌ <b>ACCESS DENIED!</b>\n\nYou haven\'t opened the Registration Link yet. Please click the "Registration" button first!',
        'play_btn': '🎮 Open Hack Menu'
    },
    'bd': {
        'earn_btn': 'কাজ শুরু করুন', 'reg_btn': '১. রেজিস্ট্রেশন লিঙ্ক ওপেন করুন', 'verify_btn': '২. আইডি ভেরিফাই করুন',
        'ask_id': '📩 আপনার প্লেয়ার আইডি দিন:', 
        'checking_steps': ['📡 সার্ভারে রিকোয়েস্ট পাঠানো হচ্ছে...', '🔍 ডাটাবেজ চেক করা হচ্ছে...', '🔑 প্রোমো কোড BLACK110 চেক হচ্ছে...'],
        'success': '✅ <b>আইডি ভেরিফাইড!</b>', 
        'fail_no_click': '❌ <b>প্রবেশ নিষেধ!</b>\n\nআপনি এখনো রেজিস্ট্রেশন লিঙ্ক ওপেন করেননি। প্রথমে "রেজিস্ট্রেশন" বাটনে ক্লিক করে একাউন্ট করুন।',
        'play_btn': '🎮 হ্যাক মেনু ওপেন করুন'
    }
}

# ================= UTILS =================
async def check_membership(user_id, context):
    try:
        m = await context.bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return m.status in [ChatMember.MEMBER, ChatMember.OWNER, ChatMember.ADMINISTRATOR]
    except: return False

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await check_membership(user_id, context):
        keyboard = [[InlineKeyboardButton("🇺🇸 English", callback_data='lang_en'), 
                     InlineKeyboardButton("🇧🇩 Bangla", callback_data='lang_bd')]]
        await update.message.reply_text("<b>Select Language:</b>", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    else:
        btn = [[InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)], [InlineKeyboardButton("✅ Joined / Verify", callback_data='check_join')]]
        await update.message.reply_text("⚠️ <b>Join our channel first!</b>", reply_markup=InlineKeyboardMarkup(btn), parse_mode='HTML')

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if await check_membership(query.from_user.id, context):
        await start(update, context)
    else:
        await query.answer("❌ You haven't joined yet!", show_alert=True)

async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = query.data.split('_')[1]
    context.user_data['lang'] = lang
    btn = [[InlineKeyboardButton(LANGUAGES[lang]['earn_btn'], callback_data='start_reg')]]
    await query.message.delete()
    await context.bot.send_photo(update.effective_chat.id, IMAGE_URL_WELCOME, caption="Click to continue.", reply_markup=InlineKeyboardMarkup(btn))

async def start_reg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'en')
    # এখানে সরাসরি লিঙ্কের বদলে আমরা একটা কলব্যাক বাটন দিচ্ছি ট্র্যাকিং এর জন্য
    btn = [[InlineKeyboardButton(LANGUAGES[lang]['reg_btn'], callback_data='click_link')],
           [InlineKeyboardButton(LANGUAGES[lang]['verify_btn'], callback_data='verify')]]
    
    caption = "<b>Step 1:</b> Click the Link button and register.\n<b>Step 2:</b> Use Promo Code: <b>BLACK110</b>\n<b>Step 3:</b> Verify your ID."
    if lang == 'bd': caption = "<b>ধাপ ১:</b> রেজিস্ট্রেশন লিঙ্ক বাটনে ক্লিক করুন।\n<b>ধাপ ২:</b> প্রোমো কোড দিন: <b>BLACK110</b>\n<b>ধাপ ৩:</b> আইডি ভেরিফাই করুন।"

    await update.callback_query.message.delete()
    await context.bot.send_photo(update.effective_chat.id, IMAGE_URL_REG, caption=caption, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(btn))

async def track_link_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ইউজার লিঙ্কে ক্লিক করলে তাকে মার্ক করা হবে এবং লিঙ্ক দেওয়া হবে"""
    user_id = update.effective_user.id
    mark_user_clicked(user_id) # ভেরিফাই ইউআইডি ফাইলে মার্ক হবে
    
    lang = context.user_data.get('lang', 'en')
    btn = [[InlineKeyboardButton("🔗 Open Registration Link", url=REG_LINK)],
           [InlineKeyboardButton("✅ I have Registered / Now Verify", callback_data='verify')]]
    
    await update.callback_query.message.reply_text("✅ <b>Link Tracked!</b>\nNow click below to register. After registration, come back and click Verify.", reply_markup=InlineKeyboardMarkup(btn), parse_mode='HTML')

async def verify_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'en')
    user_id = update.effective_user.id
    
    # চেক করবে সে কি বাটনে ক্লিক করেছিল?
    if not has_user_clicked(user_id):
        await update.callback_query.answer(LANGUAGES[lang]['fail_no_click'], show_alert=True)
        return ConversationHandler.END

    await update.callback_query.message.reply_text(LANGUAGES[lang]['ask_id'], parse_mode='HTML')
    return WAITING_FOR_ID

async def receive_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('lang', 'en')
    uid = update.message.text
    
    # এনিমেশন ফাইল থেকে কল করা হচ্ছে
    await start_verification_animation(update, context, LANGUAGES[lang])
    
    btn = [[InlineKeyboardButton(LANGUAGES[lang]['play_btn'], callback_data='hack_menu')]]
    await update.message.reply_photo(IMAGE_URL_SUCCESS, caption=LANGUAGES[lang]['success'], parse_mode='HTML', reply_markup=InlineKeyboardMarkup(btn))
    return ConversationHandler.END

async def hack_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    btn = [[InlineKeyboardButton("✈️ Aviator Hack", web_app=WebAppInfo(url="https://aviatorgameadmin.netlify.app/"))],
           [InlineKeyboardButton("💣 Mines Hack", web_app=WebAppInfo(url="https://mines-game-hack.netlify.app/"))]]
    await update.callback_query.message.delete()
    await context.bot.send_photo(update.effective_chat.id, IMAGE_URL_HACK_MENU, caption="Select Game:", reply_markup=InlineKeyboardMarkup(btn))

# (বাকি অ্যাডমিন প্যানেল এবং ব্রডকাস্ট লজিক আগের মতই থাকবে...)
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    await update.message.reply_text("👑 Admin Panel Open. Use /broadcast for messages.")

# ================= RUNNER =================
if __name__ == '__main__':
    keep_alive()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    v_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(verify_start, pattern='^verify$')],
        states={WAITING_FOR_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_id)]},
        fallbacks=[]
    )
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('admin', admin))
    application.add_handler(v_conv)
    application.add_handler(CallbackQueryHandler(track_link_click, pattern='^click_link$'))
    application.add_handler(CallbackQueryHandler(check_join, pattern='^check_join$'))
    application.add_handler(CallbackQueryHandler(language_handler, pattern='^lang_'))
    application.add_handler(CallbackQueryHandler(start_reg, pattern='^start_reg$'))
    application.add_handler(CallbackQueryHandler(hack_menu, pattern='^hack_menu$'))
    
    application.run_polling()
