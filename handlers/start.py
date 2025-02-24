from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

router = Router()


@router.message(Command("start"))
async def start_command(message: types.Message):
    """
    Обработчик команды /start
    """
    # Создаем кнопки с уникальными callback_data:
    button_expense = InlineKeyboardButton(text="расход", callback_data="add_expense")
    button_income = InlineKeyboardButton(text="доход", callback_data="add_income")
    button_stats = InlineKeyboardButton(text="стата", callback_data="view_statistics")
    button_stats_edit = InlineKeyboardButton(text="изменить", callback_data="edit_statistics")
    button_month = InlineKeyboardButton(text="месяц", callback_data="month_stats")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        button_expense,
        button_income,
        button_stats,
        button_stats_edit,
        button_month
    ]])
    await message.answer("Привет! Выберите действие:", reply_markup=keyboard)
