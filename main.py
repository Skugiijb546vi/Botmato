import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading
import time
import html
import logging
from flask import Flask, request
import os

# 🛠️ ڕێکخستنی سیستەمی لۆگ بۆ دۆزینەوەی هەڵەکان
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 🔑 وەرگرتنی تۆکن و لینک لە سێرڤەر (بۆ پاراستنی ئەمنییەت)
TOKEN = os.environ.get("TOKEN", "8602228263:AAGgll36oQCouLWd-7s903h8JY2xKRwcQ0c")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://your-app-name.onrender.com")

bot = telebot.TeleBot(TOKEN)

# 📢 لیستی چەناڵە ناچارییەکان
CHANNELS = [
    "Matounknown2",
    "matounknowndrama",
    "kurdishrevolution1",
    "DOBLAZH_k"
]

# ⚪ لیستی سپی (ئەوانەی بۆتەکە کاریان پێ نییە)
WHITELIST = {
    "matounknowngroup",
    "matodarklove"
}

def check_membership(user_id):
    """پشکنینی ئەوەی ئایا یوزەر جۆینی هەموو کەناڵەکانی کردووە؟"""
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(f"@{channel}", user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception as e:
            logger.error(f"Error checking membership for @{channel}: {e}")
            return False
    return True

@bot.message_handler(commands=['ping'])
def test_bot(message):
    bot.reply_to(message, "✅ بۆتەکە کاردەکات و سیستەمی VIP ئاکتیڤە!")

@bot.message_handler(content_types=['text', 'photo', 'video', 'sticker', 'animation', 'voice', 'video_note'], func=lambda message: message.chat.type in ['group', 'supergroup'])
def handle_group_messages(message):
    # پشکنینی ئەوەی ئەگەر نامەکە لە کەناڵەوە هاتبێت یان یوزەری سپی بێت
    if getattr(message, 'is_automatic_forward', False): return
    if message.from_user.id == 777000 or (message.sender_chat and message.sender_chat.type == 'channel'): return

    sender_username = (message.sender_chat.username if message.sender_chat else message.from_user.username)
    if sender_username and sender_username.lower() in WHITELIST: return 

    user_id = message.from_user.id

    # ئەگەر ئەدمین بوو وازی لێ بهێنە
    try:
        group_member = bot.get_chat_member(message.chat.id, user_id)
        if group_member.status in ['creator', 'administrator']: return 
    except: pass

    # ئەگەر جۆینی کردبوو وازی لێ بهێنە
    if check_membership(user_id): return

    # سڕینەوەی نامەی یوزەرەکە چونکە جۆینی نەکردووە
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except: return 

    # 🎨 دروستکردنی دوگمەکان
    markup = InlineKeyboardMarkup(row_width=2)
    btns = [
        InlineKeyboardButton("دراماکان 🎭", url="https://t.me/matounknowndrama"),
        InlineKeyboardButton("هەواڵەکان 📰", url="https://t.me/kurdishrevolution1"),
        InlineKeyboardButton("سێبەر تیڤی 📺", url="https://t.me/DOBLAZH_k")
    ]
    markup.add(btns[0], btns[1])
    markup.add(btns[2], btns[3])
    markup.row(InlineKeyboardButton("پشکنینی بەشداریکردن ✅", callback_data="check_join"))

    # 📝 نوسینی نامەی ئاگاداری بە شێوازی Blockquote
    safe_name = html.escape(message.from_user.first_name)
    warning_text = (
        f"<blockquote><b>👋 سڵاو {safe_name}</b>\n\n"
        f"🛑 <b>بۆ ناردنی نامە، دەبێت سەرەتا لە چەناڵەکانی خوارەوە جۆین بیت.</b>\n\n"
        f"⏳ <i>ئەم نامەیە دوای ٦٠ چرکە دەسڕێتەوە...</i></blockquote>"
    )

    try:
        # 🎭 ستیکەرە شازە نوێیەکەت
        NEW_STICKER_ID = "CAACAgIAAxkBAAEDb-hp9JtEtBQHYDCWyUiLJttYj5TsggAC7p4AAgzfoUtgqj5FYt-8HTsE"
        
        # ناردنی ستیکەر و پاشان نامەکە
        sent_sticker = bot.send_sticker(message.chat.id, sticker=NEW_STICKER_ID)
        sent_msg = bot.send_message(message.chat.id, warning_text, reply_markup=markup, parse_mode="HTML")
        
        # سڕینەوەی ئۆتۆماتیکی دوای خولەکێک
        threading.Timer(60.0, lambda: bot.delete_message(message.chat.id, sent_sticker.message_id)).start()
        threading.Timer(60.0, lambda: bot.delete_message(message.chat.id, sent_msg.message_id)).start()
        
    except Exception as e:
        logger.error(f"Error in sending sequence: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_callback(call):
    if check_membership(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ سوپاس! ئێستا دەتوانیت نامە بنێریت.", show_alert=True)
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
    else:
        bot.answer_callback_query(call.id, "❌ هێشتا جۆینی هەموو کەناڵەکانت نەکردووە!", show_alert=True)

# 🌐 ڕێکخستنی Flask بۆ Webhook
app = Flask(__name__)

@app.route('/')
def home(): return "Bot is Alive!"

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
