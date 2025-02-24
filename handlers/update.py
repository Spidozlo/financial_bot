from aiogram import Router, types
from aiogram.filters import Command
from database.db import add_income  # функция добавления дохода в базу
from parsers.parser_module import get_latest_income_transactions  # наш парсер

router = Router()

@router.message(Command("update"))
async def update_income_transactions(message: types.Message):
    """
    Обработчик команды /update:
    1. Получает актуальные транзакции с сайта с помощью парсера.
    2. Для каждой транзакции вызывает add_income, чтобы добавить её в таблицу доходов.
    """
    try:
        transactions = get_latest_income_transactions()
    except Exception as e:
        await message.answer(f"Ошибка при обновлении: {e}")
        return

    if not transactions:
        await message.answer("Транзакции не найдены")
        return

    count = 0
    for tr in transactions:
        # При необходимости можно добавить проверку типа транзакции или фильтрацию по терминалу
        add_income(tr["index"], tr["amount"], "", tr["terminal"])
        count += 1

    await message.answer(f"Обновлено {count} транзакций дохода.")
