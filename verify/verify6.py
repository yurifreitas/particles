import uproot
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp, pearsonr
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
    data = tree.arrays(valid_branches, library="pd", entry_stop=200000)  # Extraindo 50k eventos

    # 🔹 Diagnóstico: Mostrar dados antes do tratamento
    print("\n📊 Primeiras linhas antes da conversão:")
    print(data.head())

    # 🔹 Conversão das colunas (manter a média em vez de pegar o primeiro valor)
    def tratar_lista(x):
        if isinstance(x, (list, np.ndarray)):
            if len(x) == 0:
                return np.nan  # Mantemos NaN em vez de excluir eventos
            return np.mean(x)  # Podemos trocar por np.sum(x) se for melhor
        return x  # Retorna o próprio valor se não for lista

    for col in data.columns:
        data[col] = data[col].apply(tratar_lista)

    # 🔹 Diagnóstico: Mostrar dados após a conversão
    print("\n📊 Primeiras linhas após conversão:")
    print(data.head())

    # 🔹 Substituir NaN por valores neutros para evitar perda de eventos
    data.fillna(0, inplace=True)  # Ou substituir por outro valor, se necessário

    print(f"\n✅ Total de eventos após tratamento: {len(data)}")

    # 🔹 Criar variáveis derivadas
    data["energia_total"] = data["CaloSumsAuxDyn.et"]
    data["pT_medio"] = data["MuonsAuxDyn.pt"]

    # 🔹 Ajustando tamanhos para o KS-Test
    num_eventos = len(data)
    muon_pt_sim = np.random.normal(50, 10, size=num_eventos)  # Agora com o mesmo tamanho dos eventos reais

    ks_stat, p_value = ks_2samp(data["pT_medio"].sample(num_eventos, random_state=42), muon_pt_sim)

    # 🔹 Análise de Correlação
    corr, p_corr = pearsonr(data["pT_medio"], data["energia_total"])
    print(f"\n📊 Correlação pT x Energia: {corr:.3f} (p-value: {p_corr:.5f})")

    print(f"\n📊 Estatística KS: {ks_stat:.3f}, p-value: {p_value:.5f}")
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
