# SpartaABC HPC Setup Guide

Panduan menjalankan SpartaABC menggunakan Apptainer di HPC tanpa akses sudo/root.

---

# 1. Install Apptainer

## Clone source

```bash
git clone https://github.com/apptainer/apptainer.git
cd apptainer
```

---

## Checkout versi stabil

```bash
git checkout v1.4.5
```

---

## Build Apptainer

```bash
./mconfig --prefix=$HOME/apptainer
make -C builddir
make -C builddir install
```

---

## Tambahkan ke PATH

```bash
export PATH=$HOME/apptainer/bin:$PATH
```

Tambahkan juga ke `.bashrc`:

```bash
echo 'export PATH=$HOME/apptainer/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

---

## Verifikasi

```bash
apptainer --version
```

Output yang diharapkan (contoh):

```text
apptainer version 1.4.5
```

---

# 2. Clone Repository SpartaABC

```bash
git clone https://github.com/TanjungArs/dataset-SpartaABC.git
```

---

# 3. Download Container Image

Download file:

- `spartaabc.sif`

dari:

[Link Images SpartaABC](https://drive.google.com/file/d/1MtmEsTb2bPlOVsgoJ814-PnrVHA0KKN2/view?usp=drive_link)

atau link dibawah ini :
```text
https://drive.google.com/file/d/1MtmEsTb2bPlOVsgoJ814-PnrVHA0KKN2/view?usp=drive_link
```

---

# 4. Upload `spartaabc.sif` ke HPC

Upload file `spartaabc.sif` ke home directory HPC.

Contoh struktur:

```text
/home/username/
├── dataset-SpartaABC
└── spartaabc.sif
```

---

# 5. Membuat Script SLURM

Buat file baru:

```bash
nano sparta_generate.sh
```

Lalu copy isi berikut:

```bash
#!/bin/bash
#SBATCH --job-name=generate-spartaabc
#SBATCH --mem=30G
#SBATCH --output=slurm-%j.out

BASE_OUTPUT="$HOME/output_sparta"
mkdir -p "$BASE_OUTPUT"

START_TIME=$(date +%s)
START_HUMAN=$(date +"%Y-%m-%d %H:%M:%S")

echo "Start time : $START_HUMAN"

SEQ=8

apptainer exec \
    -B "$BASE_OUTPUT":/input \
    -B "$HOME/dataset-SpartaABC":/app \
    "$HOME/spartaabc.sif" \
    bash -c "python3 /app/msa_nuc.py \
        'MSA-$SEQ' \
        /input/ \
        32 44 \
        0.5 1.0 \
        1 \
        0.0 0.05 \
        1.01 2.0 \
        '$SEQ'"

END_TIME=$(date +%s)
END_HUMAN=$(date +"%Y-%m-%d %H:%M:%S")

DURATION=$((END_TIME - START_TIME))

echo "End time   : $END_HUMAN"
echo "Durasi     : ${DURATION} detik"
```

---

## Simpan file

Tekan:

```text
CTRL + O
ENTER
CTRL + X
```

---

## Beri izin executable

```bash
chmod +x sparta_generate.sh
```

---

## Keterangan 

```bash
apptainer exec \
    -B "$BASE_OUTPUT":/input \             # folder output HPC -> /input di container
    -B "$HOME/dataset-SpartaABC":/app \    # folder source code SpartaABC -> /app di container
    "$HOME/spartaabc.sif" \                # file image Apptainer
    bash -c "python3 /app/msa_nuc.py \     # script yang dijalankan
        'MSA-8' \                          # flag/nama folder output
        /input/ \                          # path hasil di dalam container
        32 44 \                            # min_seq_length max_seq_length
        0.5 1.0 \                          # min_branch_length max_branch_length
        10 \                               # jumlah sampel (num_of_samples)
        0.0 0.05 \                         # minIR maxIR (indel rate)
        1.01 2.0 \                         # minAVal maxAVal
        5"                                 # jumlah sekuens (num_of_sequences)
```
---

# 6. Test Generate

Jalankan:

```bash
sbatch sparta_generate.sh
```

---


# 7. Hasil Generate

Output hasil generate akan muncul pada:

```text
$HOME/output_sparta
```
