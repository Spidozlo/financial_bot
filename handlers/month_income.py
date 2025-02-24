from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import get_income_total_by_month
import re

router = Router()

class MonthIncomeState(StatesGroup):
    waiting_for_month = State()

@router.message(Command("month_income"))
async def cmd_month_income(message: types.Message, state: FSMContext):
    await message.answer("Введите месяц в формате YYYY-MM для статистики доходов:")
    await state.set_state(MonthIncomeState.waiting_for_month)

@router.message(MonthIncomeState.waiting_for_month)
async def process_month_income(message: types.Message, state: FSMContext):
    month = message.text.strip()
    if not re.fullmatch(r"\d{4}-\d{2}", month):
        await message.answer("Неверный формат. Введите месяц в формате YYYY-MM (например, 2023-03).")
        return

    terminals = ["136934", "136935"]
    overall_total = 0.0
    result_text = ""
    for term in terminals:
        total = get_income_total_by_month(term, month)
        overall_total += total
        result_text += f"Общий доход автомата № ({term}) за {month}: {total:.2f} ₽\n"
    result_text += f"\n**Общий доход за {month}: {overall_total:.2f} ₽**"
    await message.answer(result_text, parse_mode="Markdown")
    await state.clear()
