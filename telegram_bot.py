from telegram import Bot

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
BOT_TOKEN = '6475202697:AAEOwMXeYP2vumiN4e2EpjUtMRWO2XY3ZsU'
CHAT_ID = '-4028738384'  # Замените на chat_id вашей группы или пользователя

async def send_message(text):
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=text)