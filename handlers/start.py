from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

router = Router()


@router.message(Command("start"))
async def start_command(message: types.Message):
    button_expense = InlineKeyboardButton(text="1. Траты", callback_data="add_expense")
    button_income = InlineKeyboardButton(text="2. Доход", callback_data="add_income")
    button_stats = InlineKeyboardButton(text="3. Статистика", callback_data="view_statistics")
    button_stats_edit = InlineKeyboardButton(text="4. Изменить статистику", callback_data="edit_statistics")
    button_month = InlineKeyboardButton(text="5. Посмотреть траты за месяц", callback_data="month_stats")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        button_expense,
        button_income,
        button_stats,
        button_stats_edit,
        button_month
    ]])
    await message.answer("Привет! Выберите действие:\n"
                         "1. Добавить траты на автоматы\n"
                         "2. Добавить доход с автоматов\n"
                         "3. Посмотреть статистику всех трат\n"
                         "4. Изменить статистику трат\n"
                         "5. Посмотреть траты за выбранный месяц",
                         reply_markup=keyboard)
