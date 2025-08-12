from src.views import get_main_page

if __name__ == "__main__":
    result = get_main_page("2025-08-12 14:30:00")
    from pprint import pprint
    pprint(result)