import os
import subprocess
import uproot
import pyarrow.parquet as pq
import pyarrow as pa
import pandas as pd
import json
import numpy as np

INPUT_DIR = "/app/data/cern_raw"
OUTPUT_DIR = "/app/data/parquet"
CHECKPOINT_FILE = "/app/logs/parquet_checkpoint.json"

def is_valid_root_file(filepath):
    """Verifica se o arquivo ROOT é válido."""
    try:
        if not os.path.exists(filepath):
            print(f"Erro: O arquivo {filepath} não existe.")
            return False
        if os.path.getsize(filepath) == 0:
            print(f"Erro: O arquivo {filepath} está vazio.")
            return False

        with uproot.open(filepath) as file:  # Abre e fecha o arquivo automaticamente
            return True
    except Exception as e:
        print(f"Aviso: O arquivo {filepath} não é válido. Erro: {e}")
        return False

def load_checkpoint():
    try:  # Adiciona tratamento de exceções para o arquivo checkpoint
        if os.path.exists(CHECKPOINT_FILE):
            with open(CHECKPOINT_FILE, "r") as f:
                return json.load(f)
    except json.JSONDecodeError:
        print("Aviso: Arquivo de checkpoint corrompido. Criando um novo.")
    except Exception as e:
        print(f"Erro ao carregar checkpoint: {e}")

    return {}  # Retorna um dicionário vazio em caso de erro

def save_checkpoint(checkpoint):
    try:
        with open(CHECKPOINT_FILE, "w") as f:
            json.dump(checkpoint, f, indent=4)
    except Exception as e:
        print(f"Erro ao salvar checkpoint: {e}")


checkpoint = load_checkpoint()

def convert_file(input_root):
    filename = os.path.basename(input_root)
    output_parquet = os.path.join(OUTPUT_DIR, filename.replace(".root.1", ".parquet"))

    if output_parquet in checkpoint:
        print(f"✅ {output_parquet} já processado. Pulando...")
        return

    print(f"📂 Processando: {input_root}")
    try:
        with uproot.open(input_root) as file: # Abre o arquivo ROOT usando um contexto (with)
            tree = file["CollectionTree"]

            branches = [
                "MuonsAuxDyn.pt", "MuonsAuxDyn.eta", "MuonsAuxDyn.phi", "MuonsAuxDyn.charge",
                "MuonSpectrometerTrackParticlesAuxDyn.qOverP",
                "CaloSumsAuxDyn.et", "EventInfoAuxDyn.CentralityMin", "EventInfoAuxDyn.CentralityMax",
                "InDetTrackParticlesAuxDyn.qOverP",
                "PrimaryVerticesAuxDyn.x", "PrimaryVerticesAuxDyn.y", "PrimaryVerticesAuxDyn.z"
            ]
            valid_branches = [b for b in branches if b in tree.keys()]
            if not valid_branches:
                print(f"⚠️ Nenhum ramo válido encontrado no arquivo {input_root}. Pulando...")
                return

            print(f"🔹 Usando os ramos disponíveis: {valid_branches}")

            data = tree.arrays(valid_branches, library="pd") # Remove entry_stop para processar todos os eventos.

            def tratar_lista(x):
                if isinstance(x, (list, np.ndarray)):
                    return np.mean(x) if len(x) > 0 else np.nan
                return x

            for col in data.columns:
                data[col] = data[col].apply(tratar_lista)

            data.fillna(0, inplace=True)

            print(f"✅ Total de eventos processados: {len(data)}")

            table = pa.Table.from_pandas(data)
            pq.write_table(table, output_parquet)

            checkpoint[output_parquet] = True
            save_checkpoint(checkpoint)
            print(f"✅ Convertido com sucesso: {output_parquet}")

    except Exception as e:
        print(f"Erro ao processar arquivo {input_root}: {e}") # Imprime o erro específico


# Agora percorre os arquivos e converte
for filename in os.listdir(INPUT_DIR):
    if filename.endswith(".root.1"):
        file_path = os.path.join(INPUT_DIR, filename)
        if os.path.isfile(file_path) and is_valid_root_file(file_path):
            convert_file(file_path) # Passa o caminho completo do arquivo