import requests
from bs4 import BeautifulSoup
import json
import datetime
from urllib.parse import quote_plus
from config import USERNAME, PASSWORD


def login(username, password):
    login_url = "https://p.vendista.ru/Auth/Login"  # верный URL для авторизации
    session = requests.Session()
    response = session.get(login_url)
    if not response.ok:
        print("Ошибка при загрузке страницы логина")
        return None
    soup = BeautifulSoup(response.text, "lxml")
    token_input = soup.find("input", {"name": "__RequestVerificationToken"})
    csrf_token = token_input.get("value") if token_input else None

    payload = {
        "Login": username,
        "Password": password
    }
    if csrf_token:
        payload["__RequestVerificationToken"] = csrf_token

    login_response = session.post(login_url, data=payload)
    if not login_response.ok or "Необходима авторизация" in login_response.text:
        print("Ошибка авторизации")
        return None

    print("Авторизация прошла успешно!")
    return session


def get_transactions_page(session, terminal_id, page_number):
    now = datetime.datetime.now()
    date_to_str = now.strftime("%Y-%m-%d %H:%M:%S")
    date_to_url = quote_plus(date_to_str)
    transactions_url = (
        "https://p.vendista.ru/Transactions/Search?"
        "OrderByColumn=2&OrderDesc=True&ItemsOnPage=200&IntervalByColumn=&"
        "DateFrom=2025-02-10+08%3A28%3A00&DateTo={}&"
        "FilterText=&OwnerId=32256&TerminalId={}&PageNumber={}"
    ).format(date_to_url, terminal_id, page_number)
    print("Запрашиваем URL:", transactions_url)
    response = session.get(transactions_url)
    if response.ok:
        return response.text
    else:
        print(f"Ошибка при получении страницы {page_number} для терминала {terminal_id}")
        return None


def parse_transactions(html):
    soup = BeautifulSoup(html, "lxml")
    tbody = soup.select_one("tbody.font--bigger")
    if tbody is None:
        print("Таблица транзакций не найдена на этой странице")
        return []
    transactions = []
    for tr in tbody.find_all("tr"):
        row_html = str(tr)
        if "card_success.png" not in row_html:
            continue  # пропускаем неуспешные транзакции
        tds = tr.find_all("td")
        if len(tds) < 8:
            continue
        index = tds[0].get_text(strip=True)
        date_time = tds[2].get_text(strip=True)
        terminal = tds[3].get_text(strip=True)
        amount_text = tds[4].get_text(strip=True)
        amount_clean = amount_text.replace("₽", "").strip().replace(",", ".")
        try:
            amount = float(amount_clean)
        except ValueError:
            amount = None
        # Остальные поля парсить не будем, оставляем только номер автомата и сумму
        transaction = {
            "index": index,
            "date_time": date_time,
            "terminal": terminal,
            "amount": amount,
        }
        transactions.append(transaction)
    return transactions


def get_latest_income_transactions():
    """
    Авторизуется, собирает актуальные транзакции для заданных терминалов,
    фильтрует только успешные транзакции и сохраняет в JSON-файл только номер автомата и сумму.
    Если файл уже существует, новые транзакции дописываются (без повторов).
    Функция возвращает объединённый список только новых транзакций для всех терминалов.
    """
    username = USERNAME
    password = PASSWORD
    session = login(username, password)
    if session is None:
        raise Exception("Не удалось авторизоваться на сайте")

    terminal_ids = ["136934", "136935"]
    all_new_transactions = []

    for term in terminal_ids:
        filename = f"transactions_{term}.json"
        try:
            with open(filename, "r", encoding="utf-8") as f:
                existing_transactions = json.load(f)
        except Exception:
            existing_transactions = []
        # Создаём множество уже известных индексов транзакций
        existing_indices = {tr.get("index") for tr in existing_transactions}

        new_transactions = []
        page = 1
        while True:
            print(f"Получаю транзакции для терминала {term}, страница {page}")
            html = get_transactions_page(session, term, page)
            if html is None:
                break
            transactions = parse_transactions(html)
            if not transactions:
                print(f"Нет транзакций на странице {page} для терминала {term}")
                break

            # Выбираем только новые транзакции
            page_new = []
            for tr in transactions:
                if tr.get("index") not in existing_indices:
                    page_new.append(tr)
                    existing_indices.add(tr.get("index"))
            if not page_new:
                # Если на текущей странице нет новых транзакций, прекращаем цикл
                break

            new_transactions.extend(page_new)
            page += 1

        # Обновляем файл: объединяем старые транзакции с новыми
        updated_transactions = existing_transactions + new_transactions
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(updated_transactions, f, ensure_ascii=False, indent=4)
        print(f"Для терминала {term} обновлено: добавлено {len(new_transactions)} новых транзакций, всего"
              f" {len(updated_transactions)}")
        all_new_transactions.extend(new_transactions)

    return all_new_transactions


def main():
    get_latest_income_transactions()


if __name__ == "__main__":
    main()
