import re, json, sys, os

def to_spaces_format(seqs):
    if not seqs:
        return ""
    L = len(seqs[0])
    return "".join(seqs[j][i] for i in range(L) for j in range(len(seqs)))

def numbers(s):
    nums = re.findall(r"\d+", s)
    return tuple(int(n) for n in nums) if nums else (float("inf"),)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 convert_dataset.py input_folder output_path")
        sys.exit(1)

    in_folder  = sys.argv[1]
    out_path   = sys.argv[2]

    files = sorted([f for f in os.listdir(in_folder) if f.endswith(".json")],
    key=numbers)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    global_id = 1
    with open(out_path, "w", encoding="utf-8") as fout:

        for fname in files:
            print("Processing:", fname)

            with open(os.path.join(in_folder, fname), "r") as f:
                data = json.load(f)

            for sample in data:
                out = {
                    "id": global_id,
                    "seq_count": len(sample["unalign"]),
                    "unalign_string": "|".join(sample["unalign"]),
                    "aligned_string": to_spaces_format(sample["aligned"]),
                    "gap_string": to_spaces_format(sample["gap_loc"])
                }
                fout.write(json.dumps(out) + "\n")
                global_id += 1

    print("Done! Total samples:", global_id - 1)