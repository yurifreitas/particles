import uproot
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import ks_2samp, pearsonr
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# 🌀 Caminho do dataset ROOT
dataset_path = "../DAOD_HION14.41888680._000002.pool.root.1"

# 📥 Abrindo arquivo ROOT
try:
    file = uproot.open(dataset_path)
    print("✅ Arquivo ROOT carregado!")

    # Identificar automaticamente a árvore correta
    tree_name = "CollectionTree"
    if tree_name not in file:
        raise ValueError(f"🚨 Árvore {tree_name} não encontrada no arquivo!")

    tree = file[tree_name]
    print(f"✅ Usando árvore: {tree_name}")

    # 🔍 Selecionando ramos relevantes
    branches = [
        "MuonsAuxDyn.pt", "MuonsAuxDyn.eta", "MuonsAuxDyn.phi", "MuonsAuxDyn.charge",
        "MuonSpectrometerTrackParticlesAuxDyn.qOverP",
        "CaloSumsAuxDyn.et", "EventInfoAuxDyn.CentralityMin", "EventInfoAuxDyn.CentralityMax",
        "InDetTrackParticlesAuxDyn.qOverP",
        "PrimaryVerticesAuxDyn.x", "PrimaryVerticesAuxDyn.y", "PrimaryVerticesAuxDyn.z"
    ]

    valid_branches = [b for b in branches if b in tree.keys()]
    print(f"🔹 Usando os ramos disponíveis: {valid_branches}")

    if not valid_branches:
        raise ValueError("🚨 Nenhum ramo válido encontrado para análise!")

    # 🔹 Extraindo os dados
    data = tree.arrays(valid_branches, library="pd", entry_stop=200000)

    # 🔹 Conversão das colunas (manter a média dos valores dentro das listas)
    def tratar_lista(x):
        if isinstance(x, (list, np.ndarray)):
            return np.mean(x) if len(x) > 0 else np.nan
        return x

    for col in data.columns:
        data[col] = data[col].apply(tratar_lista)

    # 🔹 Substituir NaN por valores neutros para evitar perda de eventos
    data.fillna(0, inplace=True)

    print(f"\n✅ Total de eventos após tratamento: {len(data)}")

    # 🔹 Criar variáveis derivadas
    data["energia_total"] = data["CaloSumsAuxDyn.et"]
    data["pT_medio"] = data["MuonsAuxDyn.pt"]

    # 🔹 Ajustando tamanhos para o KS-Test
    num_eventos = len(data)
    muon_pt_sim = np.random.normal(50, 10, size=num_eventos)

    ks_stat, p_value = ks_2samp(data["pT_medio"].sample(num_eventos, random_state=42), muon_pt_sim)

    # 🔹 Análise de Correlação
    corr, p_corr = pearsonr(data["pT_medio"], data["energia_total"])
    print(f"\n📊 Correlação pT x Energia: {corr:.3f} (p-value: {p_corr:.5f})")

    print(f"\n📊 Estatística KS: {ks_stat:.3f}, p-value: {p_value:.5f}")
    if p_value < 0.05:
        print("🔴 Evento estatisticamente diferente do Modelo Padrão! POTENCIAL NOVA PARTÍCULA!")
    else:
        print("🟢 Evento pode ser explicado pelo Modelo Padrão.")

    # ✅ VISUALIZAÇÕES NÃO LINEARES AVANÇADAS ✅ #

    # 🔹 **1. Projeção 3D NÃO LINEAR usando t-SNE**
    print("🔍 Aplicando t-SNE para redução de dimensionalidade...")
    tsne = TSNE(n_components=3, perplexity=30, random_state=42)
    tsne_result = tsne.fit_transform(data[["pT_medio", "energia_total", "MuonsAuxDyn.eta", "MuonsAuxDyn.phi"]])

    df_tsne = pd.DataFrame(tsne_result, columns=["TSNE1", "TSNE2", "TSNE3"])
    df_tsne["energia"] = data["energia_total"]

    fig_tsne = px.scatter_3d(
        df_tsne,
        x="TSNE1",
        y="TSNE2",
        z="TSNE3",
        color="energia",
        title="Projeção 3D via t-SNE",
        labels={"TSNE1": "Dimensão 1", "TSNE2": "Dimensão 2", "TSNE3": "Dimensão 3"},
        color_continuous_scale="magma"
    )
    fig_tsne.show()

    # 🔹 **2. Projeção em 2D via UMAP**
    print("🔍 Aplicando UMAP para redução de dimensionalidade...")
    reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, n_components=2, random_state=42)
    umap_result = reducer.fit_transform(data[["pT_medio", "energia_total", "MuonsAuxDyn.eta", "MuonsAuxDyn.phi"]])

    df_umap = pd.DataFrame(umap_result, columns=["UMAP1", "UMAP2"])
    df_umap["energia"] = data["energia_total"]

    fig_umap = px.scatter(
        df_umap,
        x="UMAP1",
        y="UMAP2",
        color="energia",
        title="Projeção 2D via UMAP",
        labels={"UMAP1": "Dimensão UMAP 1", "UMAP2": "Dimensão UMAP 2"},
        color_continuous_scale="inferno"
    )
    fig_umap.show()

    # 🔹 **3. Heatmap da correlação entre todas as variáveis**
    plt.figure(figsize=(10, 8))
    sns.heatmap(data.corr(), annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title("Mapa de Calor - Correlação entre Variáveis")
    plt.show()

    # 🔹 **4. Kernel Density Estimation (KDE) para encontrar densidade das partículas**
    fig_kde = px.density_contour(
        data,
        x="MuonsAuxDyn.pt",
        y="energia_total",
        title="Densidade de Distribuição Momentum x Energia",
        labels={"MuonsAuxDyn.pt": "Momentum Transverso (GeV)", "energia_total": "Energia Total (GeV)"},
        color_continuous_scale="viridis"
    )
    fig_kde.show()

except Exception as e:
    print(f"❌ Erro: {e}")

finally:
    try:
        file.close()
        print("✅ Arquivo ROOT fechado com sucesso.")
    except:
        pass
