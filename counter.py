import json
from pathlib import Path

START_ID = 1
END_ID = 1_500_000

# Path ke folder JSON
FOLDER_PATH = Path("/home/tyudha/dataset_msa/final_dataset/data_set_MSA-5/msa-nuc-5")

found_ids = set()

# Ambil semua file .json saja (001.json ... 300.json)
json_files = sorted(FOLDER_PATH.glob("*.json"))

print(f"Total file JSON ditemukan: {len(json_files)}")

for file_path in json_files:
    print(f"Membaca {file_path.name}")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)   # sesuai contoh: list of dict

        for item in data:
            found_ids.add(item["sample_msa_id"])

print(f"Total sample_msa_id terbaca: {len(found_ids)}")

# Cari ID yang hilang
missing_ids = sorted(set(range(START_ID, END_ID + 1)) - found_ids)

print(f"Jumlah ID hilang: {len(missing_ids)}")

if missing_ids:
    print("ID yang hilang:", missing_ids)

