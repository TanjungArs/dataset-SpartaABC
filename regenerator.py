# regenerator.py
import json
import os
import sys

CHUNK_SIZE = 5000


def read(report_path):
    with open(report_path) as f:
        for line in f:
            line = line.strip()
            if line and line[0].isdigit():
                return [int(x.strip()) for x in line.split(",") if x.strip()]
    return []


def folder_name(sample_id):
    chunk_id = (sample_id - 1) // CHUNK_SIZE + 1
    return f"{chunk_id:03d}.json"


def main(folder_asli, folder_regen):
    report_path = os.path.join(folder_asli, "validation_report.txt")

    if not os.path.exists(report_path):
        print("❌ validation_report.txt tidak ditemukan")
        sys.exit(1)

    bad_ids = read(report_path)
    if not bad_ids:
        print("✅ Tidak ada sample anomali")
        return

    print(f"🔎 Sample anomali: {bad_ids}")

    regen_files = sorted(f for f in os.listdir(folder_regen) if f.endswith(".json"))
    regen_data = []
    for f in regen_files:
        with open(os.path.join(folder_regen, f)) as jf:
            regen_data.extend(json.load(jf))

    if len(regen_data) < len(bad_ids):
        print("⚠️ Data regen lebih sedikit dari jumlah anomali (lanjut sebisanya)")

    for sid, new_sample in zip(bad_ids, regen_data):
        fname = folder_name(sid)
        fpath = os.path.join(folder_asli, fname)

        if not os.path.exists(fpath):
            print(f"⚠️ {fname} tidak ditemukan, sample {sid} dilewati")
            continue

        with open(fpath) as f:
            data = json.load(f)

        target_idx = None
        for i, s in enumerate(data):
            if s.get("sample_msa_id") == sid:
                target_idx = i
                break

        if target_idx is None:
            print(f"⚠️ sample {sid} tidak ditemukan di {fname}")
            continue

        new_sample["sample_msa_id"] = sid
        data[target_idx] = new_sample

        with open(fpath, "w") as f:
            json.dump(data, f, indent=2)

        print(f"🔄 Sample {sid} diperbarui di {fname}")

    print("✅ Regenerasi selesai")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 regenerator.py <folder_json_asli> <folder_json_regen>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])