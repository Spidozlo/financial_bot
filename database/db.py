import sqlite3
# Таблица для расходов
def create_db():
    conn = sqlite3.connect('database/expenses.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            description TEXT,
            expense_datetime DATETIME DEFAULT (datetime('now','localtime'))
        )
    ''')

    # Таблица для доходов
    c.execute('''
        CREATE TABLE IF NOT EXISTS incomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_index TEXT UNIQUE,  -- уникальный идентификатор транзакции
            amount REAL,
            description TEXT,
            terminal TEXT,
            income_datetime DATETIME DEFAULT (datetime('now','localtime'))
        )
    ''')

    conn.commit()
    conn.close()

def add_expense(amount, description):
    conn = sqlite3.connect('database/expenses.db')
    c = conn.cursor()
    c.execute("INSERT INTO expenses (amount, description) VALUES (?, ?)", (amount, description,))
    conn.commit()
    conn.close()

def add_income(transaction_index, amount, description, terminal):
    # Добавляем номер автомата в описание, если хотите:
    new_description = f"{description} (автомат {terminal})"
    conn = sqlite3.connect('database/expenses.db')
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO incomes (transaction_index, amount, description, terminal) VALUES (?, ?, ?, ?)",
        (transaction_index, amount, new_description, terminal)
    )
    conn.commit()
    conn.close()



def get_statistics():
    conn = sqlite3.connect('database/expenses.db')
    c = conn.cursor()
    c.execute(
        """
        SELECT id, amount, description, expense_datetime 
        FROM expenses 
        WHERE date(expense_datetime) = date('now','localtime')
        """
    )
    expenses = c.fetchall()
    c.execute("SELECT id, amount, description FROM incomes")
    incomes = c.fetchall()
    conn.close()
    return expenses, incomes



def delete_expense(expense_id):
    conn = sqlite3.connect('database/expenses.db')
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

def update_expense(expense_id, new_amount, new_description):
    conn = sqlite3.connect('database/expenses.db')
    c = conn.cursor()
    c.execute("UPDATE expenses SET amount = ?, description = ? WHERE id = ?",
              (new_amount, new_description, expense_id))
    conn.commit()
    conn.close()

def update_expense_datetime(expense_id, new_datetime):
    conn = sqlite3.connect('database/expenses.db')
    c = conn.cursor()
    c.execute("UPDATE expenses SET expense_datetime = ? WHERE id = ?", (new_datetime, expense_id))
    conn.commit()
    conn.close()

def get_expenses_by_month(year_month):
    conn = sqlite3.connect('database/expenses.db')
    c = conn.cursor()
    # Выбираем записи, где год и месяц совпадают с заданными
    c.execute(
        "SELECT id, amount, description, expense_datetime FROM expenses WHERE strftime('%Y-%m', expense_datetime) = ?",
        (year_month,)
    )
    results = c.fetchall()
    conn.close()
    return results
import json

def get_income_total_by_month(terminal, month):
    """
    Возвращает суммарный доход для указанного терминала за месяц,
    исходя из данных, сохранённых в файле transactions_{terminal}.json.
    Параметр month должен быть в формате 'YYYY-MM'
    """
    filename = f"transactions_{terminal}.json"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            transactions = json.load(f)
    except Exception as e:
        print(f"Ошибка при чтении файла {filename}: {e}")
        return 0.0

    total = 0.0
    for tr in transactions:
        date_time = tr.get("date_time", "")
        if date_time:
            # Ожидаемый формат даты: "21.02.2025 13:38:49"
            # Извлекаем дату и преобразуем её в "YYYY-MM"
            date_part = date_time.split(" ")[0]  # "21.02.2025"
            parts = date_part.split(".")  # [ "21", "02", "2025" ]
            if len(parts) == 3:
                day, m, y = parts
                date_str = f"{y}-{m}"  # например, "2025-02"
                if date_str == month:
                    total += tr.get("amount", 0)
    return total





