import os
import subprocess
import json
import tempfile
import shutil

INPUT_DIR = "/app/data/cern_raw"
os.makedirs(INPUT_DIR, exist_ok=True)

CHECKPOINT_FILE = "/app/logs/parquet_checkpoint.json"

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return json.load(f)
    return {}

def save_checkpoint(checkpoint):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(checkpoint, f, indent=4)

checkpoint = load_checkpoint()

urls = [
    f"root://eospublic.cern.ch//eos/opendata/atlas/rucio/data15_hi/DAOD_HION14.41691899._{i:06d}.pool.root.1"
    for i in range(1, 38)
]

def download_file(url):
    filename = url.split("/")[-1]
    final_filepath = os.path.join(INPUT_DIR, filename)

    if os.path.exists(final_filepath):
        print(f"Pulando arquivo: {final_filepath} (já existe)")
        return

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_filepath = os.path.join(temp_dir, filename)
            command = ["xrdcp", url, temp_filepath]

            print(f"Baixando {filename} para {temp_filepath}")
            subprocess.run(command, check=True)
            print(f"✅ Download concluído para o diretório temporário: {temp_filepath}")

            shutil.move(temp_filepath, final_filepath)
            print(f"✅ Arquivo movido para o destino final: {final_filepath}")

    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao baixar: {url}: {e}")
    except Exception as e:
        print(f"❌ Erro geral ao processar {url}: {e}")

# Executa os downloads sequencialmente
for url in urls:
    download_file(url)

print("🎉 Todos os downloads foram concluídos!")