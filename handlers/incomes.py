from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.db import add_income

router = Router()

# --- Обработка доходов ---
class IncomeState(StatesGroup):
    amount = State()
    description = State()

@router.callback_query(lambda callback: callback.data == "add_income")
async def callback_add_income(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Введите сумму дохода:")
    await state.set_state(IncomeState.amount)

@router.message(IncomeState.amount)
async def process_income_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        await state.update_data(amount=amount)
        await message.answer("Введите описание дохода:")
        await state.set_state(IncomeState.description)
    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму (например, 100 или 50.75).")

@router.message(IncomeState.description)
async def process_income_description(message: types.Message, state: FSMContext):
    description = message.text
    data = await state.get_data()
    amount = data.get("amount")
    add_income(amount, description)
    await message.answer(f"Доход {amount} с описанием '{description}' успешно добавлен!")
    await state.clear()
