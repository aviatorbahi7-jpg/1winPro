import asyncio

# এখানে আমরা ডাটাবেজ হিসেবে একটি ডিকশনারি ব্যবহার করছি (সাময়িকভাবে)
# রিয়েল লাইফে এটা ডেটাবেজে সেভ করা ভালো
user_click_data = {}

def mark_as_clicked(user_id):
    """ইউজার যখন রেজিস্ট্রেশন লিংকে ক্লিক করবে, তখন এই ফাংশন কল হবে"""
    user_click_data[user_id] = True

async def validate_id_logic(user_id, uid):
    """আইডি ভেরিফাই করার মেইন লজিক"""
    
    # শর্ত ১: ইউজার কি লিংকে ক্লিক করেছে?
    has_clicked = user_click_data.get(user_id, False)
    
    # নাটক শুরু (যাতে ইউজার মনে করে সার্ভার চেক হচ্ছে)
    steps = ["📡 Connecting...", "🔍 Checking Referral Link...", "🔑 Verifying Promo Code..."]
    
    if not has_clicked:
        # যদি লিংকে ক্লিক না করে থাকে, তবে ২ সেকেন্ড পর রিজেক্ট করে দেবে
        return False, "REJECTED_NO_LINK"
    
    # যদি লিংকে ক্লিক করে থাকে, তবে আইডিটি সাকসেস দেখাবে
    return True, "SUCCESS"
