import json
from src.views import get_main_page

if __name__ == "__main__":
    result = get_main_page("2021-12-21 10:00:00", stock_api_key="G1QEIYEVBE15YIAY")
    print(json.dumps(result, indent=2, ensure_ascii=False))
