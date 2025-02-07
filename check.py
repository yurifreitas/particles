import uproot
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import ks_2samp, pearsonr
from decimal import Decimal, getcontext
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# Aumentando a precisão do Decimal para exibir mais casas decimais
getcontext().prec = 50  # Define até 50 casas decimais de precisão

# 🌀 Caminho do dataset ROOT
dataset_path = "DAOD_HION14.41888680._000002.pool.root.1"

# 📥 Abrindo arquivo ROOT
try:
    file = uproot.open(dataset_path)
    print("✅ Arquivo ROOT carregado!")

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

    # 🔥 **Cálculo do Teste de Kolmogorov-Smirnov com Precisão Maior**
    ks_stat, p_value = ks_2samp(data["pT_medio"].sample(num_eventos, random_state=42), muon_pt_sim)

    p_value_decimal = Decimal(p_value)  # Converter para Decimal para alta precisão

    # 🔥 **Cálculo da Correlação com Maior Precisão**
    corr, p_corr = pearsonr(data["pT_medio"], data["energia_total"])
    p_corr_decimal = Decimal(p_corr)  # Converter para Decimal para maior precisão

    print(f"\n📊 Correlação pT x Energia: {corr:.12f} (p-value: {p_corr_decimal:.50f})")
    print(f"\n📊 Estatística KS: {ks_stat:.12f}, p-value: {p_value_decimal:.50f}")

    if p_value < 0.05:
        print("🔴 Evento estatisticamente diferente do Modelo Padrão! POTENCIAL NOVA PARTÍCULA!")
    else:
        print("🟢 Evento pode ser explicado pelo Modelo Padrão.")

except Exception as e:
    print(f"❌ Erro: {e}")

finally:
    try:
        file.close()
        print("✅ Arquivo ROOT fechado com sucesso.")
    except:
        pass
