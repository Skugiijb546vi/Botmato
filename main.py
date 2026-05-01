import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading
import time
import html
import logging
from flask import Flask, request
import os

# 🛠️ ڕێکخستنی سیستەمی لۆگ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ⚠️ تۆکن و لینکی سێرڤەرەکە لە Environment Variables وەردەگرین بۆ پاراستن و ئاسانی
TOKEN = os.environ.get("TOKEN", "8602228263:AAGgll36oQCouLWd-7s903h8JY2xKRwcQ0c")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://your-app-name.onrender.com")

bot = telebot.TeleBot(TOKEN)

# لیستی چەناڵەکان کە دەبێت خەڵک جۆینی بکات
CHANNELS = [
    "Matounknown2",
    "matounknowndrama",
    "kurdishrevolution1",
    "DOBLAZH_k"
]

# ⚡ لیستی ئەو یوزەرنەیمانەی کە حوڕن
WHITELIST = {
    "matounknowngroup",
    "matodarklove"
}

def check_membership(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(f"@{channel}", user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception as e:
            logger.error(f"Error checking @{channel}: {e}")
            return False
    return True

@bot.message_handler(commands=['ping'], func=lambda message: message.chat.type in ['group', 'supergroup'])
def test_bot(message):
    bot.reply_to(message, "✅ بۆتەکە بە سیستەمی Webhook ئۆنلاینە بە دیزاینە VIP یەکەوە!")

@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker', 'animation', 'dice', 'video_note', 'contact', 'location', 'poll', 'venue'], func=lambda message: message.chat.type in ['group', 'supergroup'])
def handle_group_messages(message):
    if getattr(message, 'is_automatic_forward', False):
        return
    
    if message.from_user.id == 777000 or (message.sender_chat and message.sender_chat.type == 'channel'):
        return

    sender_username = (message.sender_chat.username if message.sender_chat else message.from_user.username)
    if sender_username and sender_username.lower() in WHITELIST:
        return 

    user_id = message.from_user.id

    try:
        group_member = bot.get_chat_member(message.chat.id, user_id)
        if group_member.status in ['creator', 'administrator']:
            return 
    except Exception as e:
        pass

    if check_membership(user_id):
        return

    try:
        bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        return 

    # 🎨 دیزاینی دوگمەکان (٢ دوگمە لە ڕیزێکدا)
    markup = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton("نەزانراو ❓", url="https://t.me/Matounknown2", style="primary")
    btn2 = InlineKeyboardButton("دراماکان 🎭", url="https://t.me/matounknowndrama", style="primary")
    btn3 = InlineKeyboardButton("هەواڵەکان 📰", url="https://t.me/kurdishrevolution1", style="primary")
    btn4 = InlineKeyboardButton("سێبەر تیڤی 📺", url="https://t.me/DOBLAZH_k", style="primary")
    
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    
    check_btn = InlineKeyboardButton("پشکنینی بەشداریکردن ✅", callback_data="check_join", style="success")
    markup.row(check_btn)

    # 🎨 دیزاینە VIP و شاهانەکەی نوسین بە Blockquote
    safe_name = html.escape(message.from_user.first_name)
    warning_text = (
        f"<blockquote><b>👋 سڵاو</b> <a href='tg://user?id={user_id}'>{safe_name}</a>\n\n"
        f"🛑 <b>پێویستە لەم چەناڵانە بەشداربیت بۆ ئەوەی بتوانیت لەم گروپە نامە بنێریت:</b>\n\n"
        f"⏳ <i>ئەم ئاگادارییە دوای ٦٠ چرکە خۆکارانە دەسڕێتەوە...</i></blockquote>"
    )

    try:
        # ١. ئایدی ستیکەرە نوێیەکەت لێرە دانرا
        STICKER_ID = "CAACAgIAAxkBAAEDb-Rp9JJaXqdiC1u5yz_aFfAOT3icFAACWaIAAmznqEuhFqjDAAG5XpA7BA"
        
        # ٢. ناردنی ستیکەرەکە
        sent_sticker = bot.send_sticker(message.chat.id, sticker=STICKER_ID)
        
        # ٣. ناردنی نامەکە لە ژێر ستیکەرەکە
        sent_msg = bot.send_message(
            message.chat.id, 
            text=warning_text, 
            reply_markup=markup, 
            parse_mode="HTML"
        )
        
        # ٤. سڕینەوەی هەردووکیان دوای ٦٠ چرکە
        threading.Timer(60.0, delete_bot_message, args=[message.chat.id, sent_sticker.message_id]).start()
        threading.Timer(60.0, delete_bot_message, args=[message.chat.id, sent_msg.message_id]).start()
        
    except Exception as e:
        logger.error(f"Error sending warning message: {e}")

def delete_bot_message(chat_id, message_id):
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        pass

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join_callback(call):
    user_id = call.from_user.id
    if check_membership(user_id):
        bot.answer_callback_query(call.id, "✅ ئێستا دەتوانیت نامە بنێریت!", show_alert=True)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception as e:
            pass
    else:
        bot.answer_callback_query(call.id, "❌ هێشتا جۆینی هەموو کەناڵەکانت نەکردووە یان لە یەکێکیان لێفتت کردووە!", show_alert=True)

# ==========================================
# 🌐 بەشی خزمەتگوزاری Flask بۆ Webhook
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot is running smoothly on Render with VIP Sticker Design!"

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=WEBHOOK_URL + '/' + TOKEN)
    logger.info(f"Webhook set to: {WEBHOOK_URL}")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
