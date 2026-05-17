import json
import os
import stat
from pathlib import Path

data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# 1. empty.csv - пустой файл для EmptyFileError
(data_dir / "empty.csv").write_text("", encoding="utf-8")
print("Created: empty.csv (empty file)")

# 2. duplicate_ids.csv - дубликаты ID для DuplicateIdError
(data_dir / "duplicate_ids.csv").write_text(
    "id,amount,category,date\n"
    "dup1,100,Category1,2024-01-01\n"
    "dup2,200,Category2,2024-01-02\n"
    "dup1,300,Category3,2024-01-03\n"
    "dup1,400,Category4,2024-01-04\n",
    encoding="utf-8"
)
print("Created: duplicate_ids.csv")

# 3. good.csv - корректный CSV
(data_dir / "good.csv").write_text(
    "id,amount,category,date\n"
    "1,100.50,Food,2024-01-15\n"
    "2,200.00,Transport,2024-01-16\n",
    encoding="utf-8"
)
print("Created: good.csv")

# 4. good.json - корректный JSON
(data_dir / "good.json").write_text(
    json.dumps([
        {"id": "3", "amount": 300.00, "category": "Salary", "date": "2024-01-17"}
    ], ensure_ascii=False, indent=2),
    encoding="utf-8"
)
print("Created: good.json")

# 5. mixed.csv - смешанные данные (валидные и с ошибками)
(data_dir / "mixed.csv").write_text(
    "id,amount,category,date\n"
    "4,500.00,Rent,2024-01-20\n"
    "5,-10.00,Food,2024-01-21\n"
    "6,abc,Clothing,2024-01-22\n"
    "7,30.00,Office,2024-01-23\n",
    encoding="utf-8"
)
print("Created: mixed.csv")

# 6. wrong.json - битый JSON для DataFormatError
(data_dir / "wrong.json").write_text(
    '{"id": "bad", "amount": 100, "category": "Test", "date": "2024-01-01"',
    encoding="utf-8"
)
print("Created: wrong.json")

# 7. no_permission.csv - для FileAccessError (убираем права на чтение)
(data_dir / "no_permission.csv").write_text(
    "id,amount,category,date\n"
    "999,1000,Test,2024-01-01\n",
    encoding="utf-8"
)
print("Created: no_permission.csv")

# Убираем права на чтение
os.chmod(data_dir / "no_permission.csv", 0o000)
print("Removed read permission: no_permission.csv")

print("\nAll test files created in data/ directory")
print("\nFiles in data/:")
for f in sorted(data_dir.glob("*")):
    size = f.stat().st_size
    print(f"  {f.name} ({size} bytes)")
