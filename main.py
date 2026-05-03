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

# 🔑 وەرگرتنی تۆکن و لینک
TOKEN = os.environ.get("TOKEN", "8602228263:AAGgll36oQCouLWd-7s903h8JY2xKRwcQ0c")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://your-app-name.onrender.com")

bot = telebot.TeleBot(TOKEN)

# 📢 لیستی چەناڵەکان
CHANNELS = [
    "matounknowndrama",
    "kurdishrevolution1",
    "DOBLAZH_k",
    "kurd_cinema5"
]

WHITELIST = {"matounknowngroup", "matodarklove"}

def check_membership(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(f"@{channel}", user_id)
            if member.status in ['left', 'kicked']: return False
        except: return False
    return True

@bot.message_handler(commands=['ping'])
def test_bot(message):
    bot.reply_to(message, "✅ بۆتەکە بەبێ کێشە کار دەکات!")

@bot.message_handler(content_types=['text', 'photo', 'video', 'sticker', 'animation', 'voice', 'video_note'], func=lambda message: message.chat.type in ['group', 'supergroup'])
def handle_group_messages(message):
    if getattr(message, 'is_automatic_forward', False): return
    if message.from_user.id == 777000 or (message.sender_chat and message.sender_chat.type == 'channel'): return
    
    sender_username = (message.sender_chat.username if message.sender_chat else message.from_user.username)
    if sender_username and sender_username.lower() in WHITELIST: return 

    user_id = message.from_user.id

    try:
        group_member = bot.get_chat_member(message.chat.id, user_id)
        if group_member.status in ['creator', 'administrator']: return 
    except: pass

    if check_membership(user_id): return

    try: bot.delete_message(message.chat.id, message.message_id)
    except: return 

    # 🎨 دیزاینی دوگمەکان
    markup = InlineKeyboardMarkup()
    CHANNEL_EMOJI_ID = "5330237710655306682" # ئیمۆجی مۆبایلەکە
    CHECK_EMOJI_ID = "5803042712919741226"   # ئیمۆجی ڕاستە پرێمیۆمەکە
    
    btn_drama = InlineKeyboardButton("دراماکان", url="https://t.me/matounknowndrama", style="primary", icon_custom_emoji_id=CHANNEL_EMOJI_ID)
    btn_news = InlineKeyboardButton("هەواڵەکان", url="https://t.me/kurdishrevolution1", style="primary", icon_custom_emoji_id=CHANNEL_EMOJI_ID)
    btn_tv = InlineKeyboardButton("سێبەر تیڤی", url="https://t.me/DOBLAZH_k", style="primary", icon_custom_emoji_id=CHANNEL_EMOJI_ID)
    btn_cinema = InlineKeyboardButton("سینەما", url="https://t.me/kurd_cinema5", style="primary", icon_custom_emoji_id=CHANNEL_EMOJI_ID)
    
    markup.row(btn_drama, btn_news)
    markup.row(btn_tv, btn_cinema)
    markup.add(InlineKeyboardButton("پشکنینی بەشداریکردن", callback_data="check_join", style="success", icon_custom_emoji_id=CHECK_EMOJI_ID))

    # 📝 نوسینی نامەکە
    safe_name = html.escape(message.from_user.first_name)
    
    # دروستکردنی ناوی بۆتەکە بە ئیمۆجییە پرێمیۆمەکان
    bot_title = (
        "<tg-emoji emoji-id='5332321341024508571'>M</tg-emoji>"
        "<tg-emoji emoji-id='5226734466315067436'>A</tg-emoji>"
        "<tg-emoji emoji-id='5332558333024934589'>T</tg-emoji>"
        "<tg-emoji emoji-id='5361583176550457135'>O</tg-emoji>"
        "<tg-emoji emoji-id='5868288832423598572'>🥇</tg-emoji> "
        "<tg-emoji emoji-id='5330453760395191684'>B</tg-emoji>"
        "<tg-emoji emoji-id='5361583176550457135'>O</tg-emoji>"
        "<tg-emoji emoji-id='5332558333024934589'>T</tg-emoji>"
    )

    new_arrow = "<tg-emoji emoji-id='5796205953913196373'>💎</tg-emoji>"
    hourglass = "<tg-emoji emoji-id='5454415424319931791'>⌛️</tg-emoji>"
    down_arrows = "".join(["<tg-emoji emoji-id='5373260879095686059'>🔽</tg-emoji>"] * 8)

    # نامەکە بەبێ هێڵەکانی (@) و بە ناوی جوڵاوەوە
    warning_text = (
        f"<blockquote><b>{bot_title}</b>\n\n"
        f"<b>سڵاو <a href='tg://user?id={user_id}'>{safe_name}</a> <tg-emoji emoji-id='5319234077457404261'>🦋</tg-emoji><tg-emoji emoji-id='5859691201250201986'>👋</tg-emoji></b>\n\n"
        f"<b>{new_arrow} بۆ ناردنی نامە، دەبێت سەرەتا لەم چەناڵانەی خوارەوە بەشداربیت:</b>\n\n"
        f"{hourglass} <i>ئەم ئاگادارییە دوای ٣ خولەک دەسڕێتەوە.</i>\n\n"
        f"{down_arrows}</blockquote>"
    )

    try:
        STICKER_ID = "CAACAgIAAxkBAAEDb-hp9JtEtBQHYDCWyUiLJttYj5TsggAC7p4AAgzfoUtgqj5FYt-8HTsE"
        
        sent_sticker = bot.send_sticker(message.chat.id, sticker=STICKER_ID)
        sent_msg = bot.send_message(message.chat.id, warning_text, reply_markup=markup, parse_mode="HTML", disable_web_page_preview=True)
        
        threading.Timer(180.0, lambda: bot.delete_message(message.chat.id, sent_sticker.message_id)).start()
        threading.Timer(180.0, lambda: bot.delete_message(message.chat.id, sent_msg.message_id)).start()
        
    except Exception as e:
        logger.error(f"Error: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_callback(call):
    if check_membership(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ دەستخۆش! ئێستا دەتوانیت نامە بنێریت.", show_alert=True)
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
    else:
        bot.answer_callback_query(call.id, "❌ هێشتا لە هەموو کەناڵەکان بەشدار نیت!", show_alert=True)

# 🌐 Flask & Webhook
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Online and cleaner than ever!"
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
