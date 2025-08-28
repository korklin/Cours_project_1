import logging
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем .env
load_dotenv()

# API ключи
CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")
STOCK_API_KEY = os.getenv("STOCK_API_KEY")

# Основная валюта
BASE_CURRENCY = os.getenv("BASE_CURRENCY", "RUB")

# Списки валют и акций
USER_CURRENCIES = os.getenv("USER_CURRENCIES", "USD,EUR,CNY").split(",")
USER_STOCKS = os.getenv("USER_STOCKS", "AAPL,GOOGL,TSLA").split(",")

# Пути
OPERATIONS_FILE = BASE_DIR / os.getenv("OPERATIONS_FILE", "data/operations.xlsx")
USER_SETTINGS_FILE = BASE_DIR / os.getenv("USER_SETTINGS_FILE", "user_settings.json")

# Логирование
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "reports.log"
# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,  # можно поменять на INFO, если не нужны DEBUG
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),  # Лог в файл
    ],
)

logger = logging.getLogger(__name__)
