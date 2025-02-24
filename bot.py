import logging
import asyncio
from aiogram import Bot, Dispatcher
from config import API_TOKEN
from handlers import start, expenses, incomes, statistics,  month_stats, update, month_income
from database.db import create_db

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Регистрируем обработчики через include_router
dp.include_router(start.router)
dp.include_router(expenses.router)
dp.include_router(incomes.router)
dp.include_router(statistics.router)
dp.include_router(month_stats.router)
dp.include_router(update.router)
dp.include_router(month_income.router)
async def on_start():
    # Создаем базу данных, если её ещё нет
    create_db()
    result = await bot.delete_webhook(drop_pending_updates=True)
    logging.info(f"Webhook удалён: {result}")
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(on_start())
    except KeyboardInterrupt:
        print('Bot остановлен')