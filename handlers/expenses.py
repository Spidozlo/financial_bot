from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.db import add_expense

router = Router()

# --- Обработка расходов ---
class ExpenseState(StatesGroup):
    amount = State()
    description = State()

@router.callback_query(lambda callback: callback.data == "add_expense")
async def callback_add_expense(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()  # убираем "часики" у кнопки
    await callback.message.answer("Введите сумму расхода:")
    await state.set_state(ExpenseState.amount)

@router.message(ExpenseState.amount)
async def process_expense_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        await state.update_data(amount=amount)
        await message.answer("Введите описание расхода:")
        await state.set_state(ExpenseState.description)
    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму (например, 100 или 50.75).")

@router.message(ExpenseState.description)
async def process_expense_description(message: types.Message, state: FSMContext):
    description = message.text
    data = await state.get_data()
    amount = data.get("amount")
    add_expense(amount, description)
    await message.answer(f"Расход {amount} с описанием '{description}' успешно добавлен!")
    await state.clear()

