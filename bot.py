import telebot
import re
import os
from threading import Thread
from flask import Flask

TOKEN = os.environ.get("9273873186:AAHW5YvXBvz5P1-uoQchvsQhU3C_i_3LY54")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is required")

app = Flask(__name__)

@app.get("/")
def health():
    return "Bot service is running", 200

def serve_http():
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port, use_reloader=False)
bot = telebot.TeleBot(TOKEN)

# ⚠️ လင့်ခ်မဖြုတ်ဘဲ တင်ခွင့်ပြုမည့် Channel တွေရဲ့ Username များကို ဤနေရာတွင် ထည့်ပါ
# ဥပမာ - '@my_channel_1', '@trusted_news' စသည်ဖြင့်
ALLOWED_CHANNELS = ['@sumo2d3d','@BawDar25','@MM2DPAY','@china2dmm','@mc2d3d','@bigbosschina','@ykb331']

def remove_links(text):
    if not text:
        return ""
    url_pattern = r'https?://\S+|www\.\S+|t\.me/\S+'
    cleaned_text = re.sub(url_pattern, '[Link]', text)
    return cleaned_text

@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'document', 'animation'])
def handle_incoming_message(message):
    if message.from_user.is_bot:
        return
        
    chat_id = message.chat.id
    text_content = message.text or message.caption
    
    # 🔍 Forward လုပ်လာတဲ့ ပို့စ် ဟုတ်မဟုတ် စစ်ဆေးခြင်း
    if message.forward_from_chat:
        forward_source = f"@{message.forward_from_chat.username}" if message.forward_from_chat.username else str(message.forward_from_chat.id)
        
        # အကယ်၍ Forward လာတဲ့ Source က ခွင့်ပြုထားတဲ့ (Allowed) Channel စာရင်းထဲ ပါနေရင်
        if forward_source in ALLOWED_CHANNELS:
            # ဘာမှ မလုပ်တော့ဘဲ ပုံမှန်အတိုင်း ဆက်တင်ခွင့်ပေးမည် (လင့်ခ်လည်း မဖြုတ်ပါ)
            return

    if text_content:
        url_pattern = r'https?://\S+|www\.\S+|t\.me/\S+'
        if re.search(url_pattern, text_content):
            
            # မူရင်း Link ပါတဲ့ Message ကို ဖျက်ခြင်း
            try:
                bot.delete_message(chat_id, message.message_id)
            except Exception as e:
                print(f"Message ဖျက်မရပါ: {e}")
                return

            # လင့်ခ်ကို ဖြုတ်ခြင်း
            cleaned_text = remove_links(text_content)
            sender_name = message.from_user.first_name or "User"
            
            announcement = f"👤 {sender_name} (Forwarded):\n\n{cleaned_text}"

            if message.photo:
                photo_id = message.photo[-1].file_id
                bot.send_photo(chat_id, photo_id, caption=announcement)
            elif message.video:
                video_id = message.video.file_id
                bot.send_video(chat_id, video_id, caption=announcement)
            else:
                bot.send_message(chat_id, announcement)

if __name__ == "__main__":
    Thread(target=serve_http, daemon=True).start()
    print("Bot အလုပ်စလုပ်နေပါပြီ...", flush=True)
    bot.infinity_polling()