from datetime import datetime, timedelta
import json
import os
import calendar
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

def get_date_range(date: datetime, range_type: str):
    if range_type == "W":
        start = date - timedelta(days=date.weekday())
        end = date
    elif range_type == "M":
        start = date.replace(day=1)
        end = date
    elif range_type == "Y":
        start = date.replace(month=1, day=1)
        end = date
    elif range_type == "ALL":
        start = datetime(2000, 1, 1)  # или earliest date
        end = date
    else:
        raise ValueError("Invalid range_type")
    return start, end

def get_greeting(date: datetime):
    hour = date.hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 17:
        return "Добрый день"
    elif 17 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"

def get_user_settings(path=None):
    if path is None:
        path = os.path.join(BASE_DIR, "user_settings.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Настройки не найдены: {path}")
    with open(path, encoding='utf-8') as f:
        return json.load(f)