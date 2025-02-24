from aiogram import Router, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from aiogram.fsm.context import FSMContext

from database.db import (
    get_statistics,
    delete_expense, update_expense,
    update_expense_datetime
)

router = Router()

@router.callback_query(lambda callback: callback.data == "view_statistics")
async def callback_view_stats(callback: types.CallbackQuery):
    await callback.answer()
    expenses, incomes = get_statistics()

    # Формируем текстовую таблицу
    stats_text = "Статистика:\n\nРасходы:\n"
    stats_text += "ID | Сумма  | Описание | Дата\n"
    stats_text += "---------------------------\n"
    if expenses:
        for exp in expenses:
            stats_text += f"{exp[0]} | {exp[1]:.2f} | {exp[2]}| {exp[3][:10]}\n"
    else:
        stats_text += "Нет записей.\n"


    # Отправляем сообщение с форматированным текстом (код-блок для моноширинного шрифта)
    await callback.message.answer(f"```{stats_text}```", parse_mode="Markdown")

@router.callback_query(lambda callback: callback.data == "edit_statistics")
async def edit_statistics_handler(callback: types.CallbackQuery):
    await callback.answer()
    expenses, incomes = get_statistics()
    # Обработка расходов с inline-кнопками для редактирования даты
    if expenses:
        await callback.message.answer("Расходы:")
        for exp in expenses:
            # Выводим дату/время (предполагается, что она находится в exp[3])
            exp_text = f"ID: {exp[0]} | Сумма: {exp[1]} | Описание: {exp[2]} | Дата: {exp[3]}"

            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(text="Редактировать", callback_data=f"edit_expense:{exp[0]}"),
                    types.InlineKeyboardButton(text="Удалить", callback_data=f"delete_expense:{exp[0]}")
                ],
                [
                    types.InlineKeyboardButton(text="Редактировать дату", callback_data=f"edit_datetime:{exp[0]}")
                ]
            ])
            await callback.message.answer(exp_text, reply_markup=keyboard)
    else:
        await callback.message.answer("Нет записей по расходам.")



# --- Обработка удаления расходов ---
@router.callback_query(lambda cb: cb.data and cb.data.startswith("delete_expense"))
async def delete_expense_handler(callback: types.CallbackQuery):
    record_id = callback.data.split(":")[1]
    delete_expense(record_id)
    await callback.answer("Расход удален!", show_alert=True)
    # Можно перезагрузить статистику
    await callback.message.answer("Обновляем статистику...")
    # Здесь можно вызвать callback_view_stats или попросить пользователя нажать кнопку "Посмотреть статистику" вновь.


# --- Обработка редактирования расходов ---
class EditExpenseState(StatesGroup):
    new_amount = State()
    new_description = State()

@router.callback_query(lambda cb: cb.data and cb.data.startswith("edit_expense"))
async def edit_expense_handler(callback: types.CallbackQuery, state: FSMContext):
    record_id = callback.data.split(":")[1]
    await state.update_data(expense_id=record_id)
    await callback.answer()
    await callback.message.answer("Введите новую сумму расхода:")
    await state.set_state(EditExpenseState.new_amount)

@router.message(EditExpenseState.new_amount)
async def process_edit_expense_amount(message: types.Message, state: FSMContext):
    try:
        new_amount = float(message.text)
        await state.update_data(new_amount=new_amount)
        await message.answer("Введите новое описание расхода:")
        await state.set_state(EditExpenseState.new_description)
    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму.")

@router.message(EditExpenseState.new_description)
async def process_edit_expense_description(message: types.Message, state: FSMContext):
    new_description = message.text
    data = await state.get_data()
    expense_id = data.get("expense_id")
    new_amount = data.get("new_amount")
    update_expense(expense_id, new_amount, new_description)
    await message.answer("Расход успешно обновлен!")
    await state.clear()


# Состояние для редактирования даты/времени расхода
class EditDateTimeState(StatesGroup):
    new_datetime = State()

@router.callback_query(lambda cb: cb.data and cb.data.startswith("edit_datetime"))
async def edit_datetime_handler(callback: types.CallbackQuery, state: FSMContext):
    record_id = callback.data.split(":")[1]
    await state.update_data(expense_id=record_id)
    await callback.answer()
    await callback.message.answer("Введите новую дату и время для расхода в формате YYYY-MM-DD HH:MM:SS:")
    await state.set_state(EditDateTimeState.new_datetime)

@router.message(EditDateTimeState.new_datetime)
async def process_edit_datetime(message: types.Message, state: FSMContext):
    new_datetime = message.text
    try:
        # Проверка формата даты и времени
        datetime_obj = datetime.strptime(new_datetime, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        await message.answer("Неверный формат. Введите дату и время в формате YYYY-MM-DD HH:MM:SS:")
        return
    data = await state.get_data()
    expense_id = data.get("expense_id")
    update_expense_datetime(expense_id, new_datetime)
    await message.answer("Дата и время расхода успешно обновлены!")
    await state.clear()
