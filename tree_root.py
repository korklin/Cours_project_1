import os

# Директории, которые игнорируем
IGNORE_DIRS = {
    ".git", ".idea", ".mypy_cache", ".pytest_cache",
    ".venv", "htmlcov", "__pycache__"
}

def print_tree(path=".", prefix=""):
    entries = sorted(os.listdir(path))
    files = [f for f in entries if os.path.isfile(os.path.join(path, f))]
    dirs = [d for d in entries if os.path.isdir(os.path.join(path, d))]

    # выводим только файлы корня
    if prefix == "":
        for f in files:
            print(f"{prefix}├── {f}")

    # выводим директории и их содержимое (только 1 уровень)
    for d in dirs:
        if d in IGNORE_DIRS:  # пропускаем ненужные
            continue
        print(f"{prefix}├── {d}/")
        sub_entries = sorted(os.listdir(os.path.join(path, d)))
        for sub in sub_entries:
            print(f"{prefix}│   ├── {sub}")

if __name__ == "__main__":
    print(os.path.basename(os.getcwd()) + "/")
    print_tree(".")
