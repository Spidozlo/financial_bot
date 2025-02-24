import re
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import get_expenses_by_month

router = Router()

# Состояние для ожидания ввода месяца
class MonthStatsState(StatesGroup):
    waiting_for_month = State()

@router.message(Command("month"))
async def cmd_month(message: types.Message, state: FSMContext):
    await message.answer("Введите месяц в формате YYYY-MM, для которого хотите узнать расходы:")
    await state.set_state(MonthStatsState.waiting_for_month)

@router.message(MonthStatsState.waiting_for_month)
async def process_month_stats(message: types.Message, state: FSMContext):
    month = message.text.strip()
    # Проверка формата "YYYY-MM"
    if not re.fullmatch(r"\d{4}-\d{2}", month):
        await message.answer("Неверный формат. Введите месяц в формате YYYY-MM (например, 2023-03).")
        return

    expenses = get_expenses_by_month(month)
    if expenses:
        stats_text = f"Расходы за {month}:\n"
        stats_text += "ID | Сумма  | Описание | Дата\n"
        stats_text += "-------------------------------------\n"
        summ = 0
        for exp in expenses:
            # Берем только дату (первые 10 символов, если формат "YYYY-MM-DD HH:MM:SS")
            date_only = exp[3][:10] if exp[3] else "N/A"
            stats_text += f"{exp[0]} | {exp[1]:.2f} | {exp[2]} | {date_only}\n"
            summ += exp[1]
        # Добавляем итоговую сумму в конце
        stats_text += "-------------------------------------\n"
        stats_text += f"Итого: {summ:.2f} рублей\n"
        await message.answer(f"```{stats_text}```", parse_mode="Markdown")
    else:
        await message.answer(f"За {month} нет записей расходов.")
    await state.clear()

@router.callback_query(lambda cb: cb.data == "month_stats")
async def month_stats_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()  # убираем "часики" у кнопки
    await callback.message.answer("Введите месяц в формате YYYY-MM, для которого хотите узнать расходы:")
    await state.set_state(MonthStatsState.waiting_for_month)
