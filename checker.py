# checker.py
import os
import json
import sys

def validate_folder(msa_chunk_dir):
    report_path = os.path.join(msa_chunk_dir, "validation_report.txt")
    bad_ids = []

    json_files = sorted(
        f for f in os.listdir(msa_chunk_dir)
        if f.endswith(".json")
    )

    expected_n = None

    for fname in json_files:
        fpath = os.path.join(msa_chunk_dir, fname)

        try:
            with open(fpath) as f:
                data = json.load(f)
        except Exception:
            continue

        for sample in data:
            aligned = sample.get("aligned", [])
            unalign = sample.get("unalign", [])
            sid = sample.get("sample_msa_id")

            # tentukan expected_n sekali saja
            if expected_n is None:
                if aligned:
                    expected_n = len(aligned)
                continue

            # hanya cek unalign
            if len(unalign) != expected_n:
                bad_ids.append(str(sid))

    with open(report_path, "w") as f:
        if bad_ids:
            f.write("⚠️ sample bermasalah :\n")
            f.write(", ".join(bad_ids) + "\n\n")
            f.write(f"Total sample bermasalah: {len(bad_ids)}\n")
        else:
            f.write("✅ Semua sample valid\n")

    return bad_ids


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python checker.py <msa_chunk_dir>")
        sys.exit(1)

    msa_chunk_dir = sys.argv[1]
    bad_ids = validate_folder(msa_chunk_dir)

    if bad_ids:
        print("⚠️ sample bermasalah :")
        print(", ".join(bad_ids))
        print(f"\nTotal sample bermasalah: {len(bad_ids)}")
    else:
        print("✅ Semua sample valid")
