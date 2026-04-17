import logging
import asyncio
import os
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember, WebAppInfo
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler

# আমাদের কাস্টম ফাইল ইম্পোর্ট করছি
from database_logic import verify_uid_from_server, check_eligibility

# লগিং সেটআপ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

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
REQUIRED_CHANNEL = int(os.getenv("REQUIRED_CHANNEL", "-1001481593780"))
CHANNEL_LINK = "https://t.me/+3U0nMzWs4Aw0YjFl"

# Images
IMAGE_URL_REG = "https://i.ibb.co/PZ5VTZVT/IMG-20260201-052425-386.jpg"
IMAGE_URL_SUCCESS = "https://i.ibb.co/fdwt2s8D/file-00000000973471faba7ce65cd5c96718.png"

WAITING_FOR_ID = 1

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    btn = [[InlineKeyboardButton("🚀 Start Registration", callback_data='start_reg')]]
    await update.message.reply_text("👋 <b>Welcome!</b>\nTo use this hack, you must have an account under our <b>Official Partner Program</b>.", reply_markup=InlineKeyboardMarkup(btn), parse_mode='HTML')

async def start_reg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    btn = [[InlineKeyboardButton("🔗 Register Now", url="https://1wezue.com/casino")],
           [InlineKeyboardButton("✅ I have Registered / Verify ID", callback_data='verify')]]
    
    caption = (
        "<b>⚠️ Verification Rules:</b>\n\n"
        "1. Click 'Register Now' and create a NEW account.\n"
        "2. Must use Promo Code: <b>BLACK110</b>\n"
        "3. If you don't use the code, your ID will be <b>REJECTED</b> by the server.\n\n"
        "<i>Already registered? Send your ID for verification.</i>"
    )
    await update.callback_query.message.delete()
    await context.bot.send_photo(update.effective_chat.id, IMAGE_URL_REG, caption=caption, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(btn))

async def verify_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("📩 <b>Please send your 8-9 digit Player ID:</b>", parse_mode='HTML')
    return WAITING_FOR_ID

async def receive_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.text
    
    if not check_eligibility(uid):
        await update.message.reply_text("❌ <b>Verification Failed!</b>\n\nThis ID was not found in our partner database. Make sure you used promo code <b>BLACK110</b> while registering.", parse_mode='HTML')
        return ConversationHandler.END

    # ভেরিফিকেশন এনিমেশন শুরু
    status_msg = await update.message.reply_text("⏳ <b>Initializing Server Connection...</b>", parse_mode='HTML')
    
    steps = await verify_uid_from_server(uid)
    for step in steps:
        await asyncio.sleep(2) # প্রতি ২ সেকেন্ড পর পর আপডেট হবে
        await status_msg.edit_text(f"⏳ <b>{step}</b>", parse_mode='HTML')
    
    await asyncio.sleep(1)
    await status_msg.delete()
    
    # ফাইনাল সাকসেস মেসেজ
    btn = [[InlineKeyboardButton("🎮 Open Hack Panel", web_app=WebAppInfo(url="https://aviatorgameadmin.netlify.app/"))]]
    await update.message.reply_photo(
        IMAGE_URL_SUCCESS, 
        caption=f"✅ <b>ID VERIFIED SUCCESSFULLY!</b>\n\n<b>ID:</b> {uid}\n<b>Status:</b> Active Partner\n\nYou can now use the hack features.", 
        parse_mode='HTML', 
        reply_markup=InlineKeyboardMarkup(btn)
    )
    return ConversationHandler.END

# ================= MAIN =================
if __name__ == '__main__':
    keep_alive()
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    
    v_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(verify_start, pattern='^verify$')],
        states={WAITING_FOR_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_id)]},
        fallbacks=[]
    )
    
    app_bot.add_handler(CommandHandler('start', start))
    app_bot.add_handler(v_conv)
    app_bot.add_handler(CallbackQueryHandler(start_reg, pattern='^start_reg$'))
    
    print("Bot is running...")
    app_bot.run_polling()
