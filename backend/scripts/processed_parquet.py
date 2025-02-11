import os
import dask.dataframe as dd
import pandas as pd
import numpy as np
import json
from sklearn.preprocessing import StandardScaler
import umap
from hdbscan import HDBSCAN
import networkx as nx

# Diretório para salvar os arquivos processados
PROCESSED_PARQUET_DIR = "/app/data/processed_parquet_parts"
CHECKPOINT_FILE = "/app/logs/processing_checkpoint.json"

# Criar diretório se não existir
os.makedirs(PROCESSED_PARQUET_DIR, exist_ok=True)
def is_valid_root_file(filepath):
    """Verifica se o arquivo ROOT é válido antes de abrir com uproot."""
    try:
        if not os.path.exists(filepath):
            print(f"Erro: O arquivo {filepath} não existe.")
            return False
        if os.path.getsize(filepath) == 0:
            print(f"Erro: O arquivo {filepath} está vazio.")
            return False

        import uproot
        with uproot.open(filepath) as file:
            return True  # Se abrir sem erro, é válido
    except Exception as e:
        print(f"Aviso: O arquivo {filepath} não é válido. Erro: {e}")
        return False
def load_checkpoint():
    """Carrega o progresso do processamento para evitar reprocessamento."""
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return json.load(f)
    return {}

def save_checkpoint(checkpoint):
    """Salva o progresso do processamento."""
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(checkpoint, f, indent=4)

def generate_fractal_connections(n=1000, depth=3):
    """
    Gera conexões fractais complexas simulando hiperdimensionalidade.

    :param n: Número de pontos.
    :param depth: Profundidade da estrutura fractal.
    :return: DataFrame representando as conexões.
    """
    G = nx.Graph()

    for i in range(n):
        G.add_node(i)
        if i > 0:
            parent = i // (2 + np.random.randint(0, 2))
            G.add_edge(i, parent)

    for _ in range(depth):
        edges = list(G.edges())
        for edge in edges:
            a, b = edge
            mid = len(G.nodes)
            G.add_node(mid)
            G.add_edge(a, mid)
            G.add_edge(mid, b)
            G.remove_edge(a, b)

    # Criando estrutura para armazenar no Parquet
    fractal_data = {
        "node": [],
        "parent": []
    }
    for edge in G.edges():
        fractal_data["node"].append(edge[0])
        fractal_data["parent"].append(edge[1])

    return pd.DataFrame(fractal_data)

def process_parquet_file(input_file, checkpoint):
    """
    Processa um único arquivo Parquet e salva de forma incremental.

    :param input_file: Caminho do arquivo Parquet original.
    :param checkpoint: Dicionário de checkpoint.
    """
    file_name = os.path.basename(input_file)
    output_file = os.path.join(PROCESSED_PARQUET_DIR, file_name)

    if file_name in checkpoint:
        print(f"✅ Já processado: {file_name}, pulando...")
        return

    print(f"📂 Processando: {file_name}")

    df = dd.read_parquet(input_file).compute()

    # Aplicar UMAP para redução de dimensionalidade
    if 'U1' not in df.columns or 'U2' not in df.columns or 'U3' not in df.columns:
        print(f"⚠️ Aplicando UMAP para redução de dimensionalidade...")
        umap_reducer = umap.UMAP(n_neighbors=50, min_dist=0.02, n_components=3, random_state=None)
        df[['U1', 'U2', 'U3']] = umap_reducer.fit_transform(df[['MuonsAuxDyn.pt', 'MuonsAuxDyn.eta', 'MuonsAuxDyn.phi']])
        print(f"✅ UMAP concluído.")

    # Aplicar HDBSCAN para clustering
    if 'cluster' not in df.columns:
        print(f"⚠️ Aplicando HDBSCAN para clustering...")
        scaler = StandardScaler()
        df_scaled = scaler.fit_transform(df[['MuonsAuxDyn.pt', 'MuonsAuxDyn.eta', 'MuonsAuxDyn.phi']])
        clusterer = HDBSCAN(min_cluster_size=10)
        df['cluster'] = clusterer.fit_predict(df_scaled)
        print(f"✅ Clustering concluído.")

    # Adicionando conexões fractais
    fractal_df = generate_fractal_connections(n=len(df), depth=3)
    df = pd.concat([df.reset_index(drop=True), fractal_df.reset_index(drop=True)], axis=1)

    # Salvando o arquivo processado
    df.to_parquet(output_file, index=False)
    print(f"✅ Arquivo salvo: {output_file}")

    # Atualizar checkpoint
    checkpoint[file_name] = True
    save_checkpoint(checkpoint)

def process_all_parquet_files(input_dir):
    """
    Processa todos os arquivos Parquet e os salva em partes para evitar estouro de memória.

    :param input_dir: Diretório contendo arquivos Parquet brutos.
    """
    checkpoint = load_checkpoint()

    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith(".parquet"):
            process_parquet_file(os.path.join(input_dir, filename), checkpoint)

if __name__ == "__main__":
    input_parquet_dir = "/app/data/parquet/"
    process_all_parquet_files(input_parquet_dir)
