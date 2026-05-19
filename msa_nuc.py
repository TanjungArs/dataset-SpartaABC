# msa_nuc.py 
from pipeline_click import pipeline
import sys
import os
import random
import string
import json
import shutil
import checker
from ete3 import Tree

def make_dummy_sample(sample_id):
    zero_param = {
        "RL": 0, "AIR": 0, "ADR": 0, "IR": 0, "DR": 0,
        "AVG_GAP_SIZE": 0, "MSA_LEN": 0, "MSA_MAX_LEN": 0, "MSA_MIN_LEN": 0,
        "TOT_NUM_GAPS": 0, "NUM_GAPS_LEN_ONE": 0, "NUM_GAPS_LEN_TWO": 0,
        "NUM_GAPS_LEN_THREE": 0, "NUM_GAPS_LEN_AT_LEAST_FOUR": 0,
        "AVG_UNIQUE_GAP_SIZE": 0, "TOT_NUM_UNIQE_GAPS": 0,
        "NUM_GAPS_LEN_ONE_POS_1_GAPS": 0,
        "NUM_GAPS_LEN_ONE_POS_2_GAPS": 0,
        "NUM_GAPS_LEN_ONE_POS_N_MINUS_1_GAPS": 0,
        "NUM_GAPS_LEN_TWO_POS_1_GAPS": 0,
        "NUM_GAPS_LEN_TWO_POS_2_GAPS": 0,
        "NUM_GAPS_LEN_TWO_POS_N_MINUS_1_GAPS": 0,
        "NUM_GAPS_LEN_THREE_POS_1_GAPS": 0,
        "NUM_GAPS_LEN_THREE_POS_2_GAPS": 0,
        "NUM_GAPS_LEN_THREE_POS_N_MINUS_1_GAPS": 0,
        "NUM_GAPS_LEN_AT_LEAST_FOUR_POS_1_GAPS": 0,
        "NUM_GAPS_LEN_AT_LEAST_FOUR_POS_2_GAPS": 0,
        "NUM_GAPS_LEN_AT_LEAST_FOUR_POS_N_MINUS_1_GAPS": 0,
        "MSA_POSITION_WITH_0_GAPS": 0,
        "MSA_POSITION_WITH_1_GAPS": 0,
        "MSA_POSITION_WITH_2_GAPS": 0,
        "MSA_POSITION_WITH_N_MINUS_1_GAPS": 0,
        "Phylogenetic_tree": ""
    }

    return {
        "sample_msa_id": sample_id,
        "parameter": [zero_param],
        "unalign": ["A"],
        "aligned": ["-"],
        "gap_loc": ["#"]
    }

flag = sys.argv[1]
path = sys.argv[2]
min_seq_length = int(sys.argv[3])
max_seq_length = int(sys.argv[4])
min_brach_length = float(sys.argv[5])
max_brach_length = float(sys.argv[6])
num_of_samples = int(sys.argv[7])
input_minIR = float(sys.argv[8])
input_maxIR = float(sys.argv[9])
input_minAVal = float(sys.argv[10])
input_maxAVal = float(sys.argv[11])
num_of_sequences = int(sys.argv[12])
pipeline_path = "/app/"
res_path = os.path.join(path, f"res_{flag}")
data_set_path = os.path.join(path, f"data_set_{flag}")
msa_chunk_dir = os.path.join(data_set_path, f"msa-nuc-{num_of_sequences}")

os.makedirs(res_path, exist_ok=True)
os.makedirs(msa_chunk_dir, exist_ok=True)

checkpoint_file = os.path.join(data_set_path, "checkpoint.json")
report_file = os.path.join(data_set_path, "validation_report.txt")

CHUNK_SIZE = 5000
chunk_data = []
start_sample = 0
chunk_id = 0

if os.path.exists(checkpoint_file):
    with open(checkpoint_file) as f:
        ckpt = json.load(f)
        
    last_completed = ckpt.get("last_completed_sample", 0)

    completed_chunks = last_completed // CHUNK_SIZE
    start_sample = completed_chunks * CHUNK_SIZE
    chunk_id = completed_chunks

    print(f"🔁 Resume aligned: start_sample={start_sample + 1}, chunk_id={chunk_id}")

msa_filename = "temp_msa.fasta"
tree_filename = "temp_tree.tree"
msa_path = os.path.join(res_path, msa_filename)
tree_path = os.path.join(res_path, tree_filename)
for sample in range(start_sample, num_of_samples):
    try:
        seq_length = random.randint(min_seq_length, max_seq_length)
        minRL = seq_length * 0.8
        maxRL = seq_length * 1.1

        t = Tree()
        seq_names = list(string.ascii_uppercase[:num_of_sequences])
        t.populate(num_of_sequences, seq_names)
        for node in t.traverse():
            if not node.is_root():
                node.dist = random.uniform(min_brach_length, max_brach_length)
        tree = t.write(format=1)
        open(tree_path, "w").write(tree)

        with open(msa_path, "w") as f:
            for name in seq_names:
                f.write(f">{name}\n{'T'*seq_length}\n")

        skip_config = {
            "sparta": True,
            "mafft": True,
            "inference": True,
            "correct_bias": True
        }

        submodel_params_ = {
            "mode": "nuc",
            "submodel": "GTR",
            "freq": (0.369764, 0.165546, 0.306709, 0.157981),
            "rates": (0.443757853, 0.084329474, 0.115502265, 0.107429571, 0.000270340),
            "inv_prop": 0.0,
            "gamma_shape": 99.852225,
            "gamma_cats": 4
        }

        unaligned_msa, aligned_msa, structure_msa = pipeline(
            skip_config=skip_config,
            pipeline_path=pipeline_path,
            res_dir=res_path,
            clean_run=False,
            msa_filename=msa_filename,
            tree_filename=tree_filename,
            minIR=input_minIR,
            maxIR=input_maxIR,
            minAVal=input_minAVal,
            maxAVal=input_maxAVal,
            minRL=minRL,
            maxRL=maxRL,
            op_sys="linux",
            verbose=0,
            b_num_top=1,
            num_alignments=1,
            filter_p=(0.9, 15),
            submodel_params=submodel_params_,
            num_simulations=1,
            num_burnin=1
        )

        params_file = os.path.join(res_path, "SpartaABC_data_name_iddif.posterior_params")
        summary_stat = open(params_file).readlines()[4].strip().split("\t")[1:]

        param_names = [
            "RL","AIR","ADR","IR","DR","AVG_GAP_SIZE","MSA_LEN","MSA_MAX_LEN","MSA_MIN_LEN",
            "TOT_NUM_GAPS","NUM_GAPS_LEN_ONE","NUM_GAPS_LEN_TWO","NUM_GAPS_LEN_THREE",
            "NUM_GAPS_LEN_AT_LEAST_FOUR","AVG_UNIQUE_GAP_SIZE","TOT_NUM_UNIQE_GAPS",
            "NUM_GAPS_LEN_ONE_POS_1_GAPS","NUM_GAPS_LEN_ONE_POS_2_GAPS",
            "NUM_GAPS_LEN_ONE_POS_N_MINUS_1_GAPS","NUM_GAPS_LEN_TWO_POS_1_GAPS",
            "NUM_GAPS_LEN_TWO_POS_2_GAPS","NUM_GAPS_LEN_TWO_POS_N_MINUS_1_GAPS",
            "NUM_GAPS_LEN_THREE_POS_1_GAPS","NUM_GAPS_LEN_THREE_POS_2_GAPS",
            "NUM_GAPS_LEN_THREE_POS_N_MINUS_1_GAPS",
            "NUM_GAPS_LEN_AT_LEAST_FOUR_POS_1_GAPS",
            "NUM_GAPS_LEN_AT_LEAST_FOUR_POS_2_GAPS",
            "NUM_GAPS_LEN_AT_LEAST_FOUR_POS_N_MINUS_1_GAPS",
            "MSA_POSITION_WITH_0_GAPS","MSA_POSITION_WITH_1_GAPS",
            "MSA_POSITION_WITH_2_GAPS","MSA_POSITION_WITH_N_MINUS_1_GAPS"
        ]

        param_dict = {
            name: summary_stat[i] if i < len(summary_stat) else None
            for i, name in enumerate(param_names)
        }
        param_dict["Phylogenetic_tree"] = tree


        data_json = {
            "sample_msa_id": sample + 1,
            "parameter": [param_dict],
            "unalign": [l for l in unaligned_msa.split("\n") if l and not l.startswith(">")],
            "aligned": [l for l in aligned_msa.split("\n") if l and not l.startswith(">")],
            "gap_loc": [l.replace("A", "#") for l in structure_msa.split("\n") if l and not l.startswith(">")]
        }

        chunk_data.append(data_json)

        if len(chunk_data) >= CHUNK_SIZE:
            chunk_id += 1
            chunk_file = os.path.join(msa_chunk_dir, f"{chunk_id:03d}.json")
            json.dump(chunk_data, open(chunk_file, "w"), indent=2)
            chunk_data.clear()

        json.dump(
            {"last_completed_sample": sample + 1, "last_chunk_id": chunk_id},
            open(checkpoint_file, "w")
        )

        print(f"✅ Sample {sample+1}/{num_of_samples}")

    except Exception as e:
        print(f"⚠️ Sample {sample+1} gagal: {e}")

if chunk_data:
    chunk_id += 1
    chunk_file = os.path.join(msa_chunk_dir, f"{chunk_id:03d}.json")
    json.dump(chunk_data, open(chunk_file, "w"), indent=2)

checker.validate_folder(msa_chunk_dir)

shutil.rmtree(res_path, ignore_errors=True)

print("\nSelesai")
