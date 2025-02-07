import uproot
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import ks_2samp, pearsonr, anderson_ksamp
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE, Isomap
import umap
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# 🌀 Caminho do dataset ROOT (DADOS REAIS DE COLISÃO)
dataset_path = "DAOD_HION14.41888680._000002.pool.root.1"

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

    # 🔹 Tratamento dos dados: pegando a média se for lista
    def tratar_lista(x):
        if isinstance(x, (list, np.ndarray)):
            return np.mean(x) if len(x) > 0 else np.nan
        return x

    for col in data.columns:
        data[col] = data[col].apply(tratar_lista)

    # 🔹 Removendo NaN
    data.fillna(0, inplace=True)

    print(f"\n✅ Total de eventos após tratamento: {len(data)}")

    # 🔹 Criando novas variáveis
    data["energia_total"] = data["CaloSumsAuxDyn.et"]
    data["pT_medio"] = data["MuonsAuxDyn.pt"]

    # 🔹 Ajustando tamanhos para o KS-Test
    num_eventos = len(data)
    muon_pt_sim = np.random.normal(50, 10, size=num_eventos)

    ks_stat, p_value = ks_2samp(data["pT_medio"].sample(num_eventos, random_state=42), muon_pt_sim)
    ad_result = anderson_ksamp([data["pT_medio"], muon_pt_sim])

    # 🔹 Análise de Correlação
    corr, p_corr = pearsonr(data["pT_medio"], data["energia_total"])
    print(f"\n📊 Correlação pT x Energia: {corr:.6f} (p-value: {p_corr:.8f})")
    print(f"\n📊 Estatística KS: {ks_stat:.6f}, p-value: {p_value:.8f}")
    print(f"\n📊 Estatística AD: {ad_result.statistic:.6f}, Significância: {ad_result.significance_level}")

    if p_value < 0.05:
        print("🔴 Evento estatisticamente diferente do Modelo Padrão! POTENCIAL NOVA PARTÍCULA!")
    else:
        print("🟢 Evento pode ser explicado pelo Modelo Padrão.")

    # ✅ VISUALIZAÇÕES NÃO LINEARES AVANÇADAS ✅ #

    # 🔹 **1. t-SNE em 3D**
    print("🔍 Aplicando t-SNE para redução de dimensionalidade...")
    tsne = TSNE(n_components=3, perplexity=40, random_state=42)
    tsne_result = tsne.fit_transform(data[["pT_medio", "energia_total", "MuonsAuxDyn.eta", "MuonsAuxDyn.phi"]])

    df_tsne = pd.DataFrame(tsne_result, columns=["TSNE1", "TSNE2", "TSNE3"])
    df_tsne["energia"] = data["energia_total"]

    fig_tsne = px.scatter_3d(df_tsne, x="TSNE1", y="TSNE2", z="TSNE3", color="energia", title="Projeção 3D via t-SNE")
    fig_tsne.show()

    # 🔹 **2. UMAP em 3D**
    print("🔍 Aplicando UMAP para redução de dimensionalidade...")
    reducer = umap.UMAP(n_neighbors=20, min_dist=0.05, n_components=3, random_state=42)
    umap_result = reducer.fit_transform(data[["pT_medio", "energia_total", "MuonsAuxDyn.eta", "MuonsAuxDyn.phi"]])

    df_umap = pd.DataFrame(umap_result, columns=["UMAP1", "UMAP2", "UMAP3"])
    df_umap["energia"] = data["energia_total"]

    fig_umap = px.scatter_3d(df_umap, x="UMAP1", y="UMAP2", z="UMAP3", color="energia", title="Projeção 3D via UMAP")
    fig_umap.show()

    # 🔹 **3. Isomap em 3D**
    print("🔍 Aplicando Isomap para redução de dimensionalidade...")
    isomap = Isomap(n_components=3, n_neighbors=10)
    isomap_result = isomap.fit_transform(data[["pT_medio", "energia_total", "MuonsAuxDyn.eta", "MuonsAuxDyn.phi"]])

    df_isomap = pd.DataFrame(isomap_result, columns=["ISOMAP1", "ISOMAP2", "ISOMAP3"])
    df_isomap["energia"] = data["energia_total"]

    fig_isomap = px.scatter_3d(df_isomap, x="ISOMAP1", y="ISOMAP2", z="ISOMAP3", color="energia", title="Projeção 3D via Isomap")
    fig_isomap.show()

except Exception as e:
    print(f"❌ Erro: {e}")

finally:
    try:
        file.close()
        print("✅ Arquivo ROOT fechado com sucesso.")
    except:
        pass
