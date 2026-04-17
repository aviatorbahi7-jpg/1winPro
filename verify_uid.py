import asyncio
import os

CLICK_FILE = "clicked_users.txt"

def mark_user_clicked(user_id):
    """ইউজার যখন রেজিস্ট্রেশন লিঙ্কে ক্লিক করার বাটনে চাপ দিবে, তাকে সেভ করা হবে"""
    if not os.path.exists(CLICK_FILE): open(CLICK_FILE, "w").close()
    with open(CLICK_FILE, "r") as f: users = f.read().splitlines()
    if str(user_id) not in users:
        with open(CLICK_FILE, "a") as f: f.write(f"{user_id}\n")

def has_user_clicked(user_id):
    """চেক করবে ইউজার কি লিঙ্কে ক্লিক করার বাটনে আগে চেপেছিল?"""
    if not os.path.exists(CLICK_FILE): return False
    with open(CLICK_FILE, "r") as f: users = f.read().splitlines()
    return str(user_id) in users

async def start_verification_animation(update, context, lang_data):
    """সার্ভার কানেক্টিং এর একটি রিয়ালিস্টিক এনিমেশন"""
    msg = await update.message.reply_text("⏳ <b>Connecting to Partner Server...</b>", parse_mode='HTML')
    
    steps = lang_data['checking_steps']
    for step in steps:
        await asyncio.sleep(2)
        await msg.edit_text(f"⏳ <b>{step}</b>", parse_mode='HTML')
    
    await asyncio.sleep(1)
    await msg.delete()
