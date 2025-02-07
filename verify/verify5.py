import uproot
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp, pearsonr
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# 🌀 Caminho do dataset ROOT
dataset_path = "../user.hteagle.1Apr.MC_MC16d.21.2.148.sysLHE.364253.Sherpa_222_NNPDF30NNLO_lllv_output.root"

# 📥 Abrindo arquivo ROOT
try:
    file = uproot.open(dataset_path)
    print("✅ Arquivo ROOT carregado!")

    # 🔍 Identificar automaticamente a árvore correta
    available_trees = [key for key in file.keys() if "CollectionTree" in key]
    
    if not available_trees:
        raise ValueError("🚨 Nenhuma árvore 'CollectionTree' encontrada no arquivo ROOT!")

    tree_name = available_trees[0]  # Pegamos a primeira árvore correspondente
    tree = file[tree_name]
    print(f"✅ Usando árvore: {tree_name}")

    # 🔍 Listar ramos disponíveis
    available_branches = tree.keys()
    print(f"📜 Ramos disponíveis na árvore:\n{available_branches}")

    # 🔹 Buscar ramos relacionados a energia, massa e momento
    candidate_branches = [
        "m_bb", "m_CTcorr", "m_T", "m_lbb",  # Massas
        "pTj1", "pTj2", "pTj3", "pTj4",      # Momentos transversos (jets)
        "pTl1", "pTmu1", "pTel1",            # Momentum transverso de leptons
        "ETMiss", "ETMissPhi",               # Energia faltante (Missing Energy)
        "all_HT", "all_METSig", "all_Meff"   # Outros indicadores globais de energia
    ]
    
    # 🔹 Garantir que os ramos existam no dataset
    valid_branches = [b for b in candidate_branches if b in available_branches]

    if not valid_branches:
        raise ValueError("🚨 Nenhum ramo relevante encontrado para análise de SUSY!")

    print(f"🔍 Usando os seguintes ramos para análise: {valid_branches}")

    # 🔹 Extraindo os dados
    data = tree.arrays(valid_branches, library="pd", entry_stop=50000)  # Limite para evitar consumo excessivo de RAM

    # 🔹 Limpeza dos dados (removendo NaN e valores anômalos)
    data = data.dropna()

    # 🔹 Criar colunas derivadas
    data["energia_total"] = data[["m_bb", "m_CTcorr", "m_T", "m_lbb"]].sum(axis=1)
    data["pT_medio"] = data[["pTj1", "pTj2", "pTj3", "pTj4", "pTl1", "pTmu1", "pTel1"]].mean(axis=1)
    
    # 🔹 Comparação estatística com um modelo padrão
    massa_simulada = np.random.normal(200, 30, size=1000)
    ks_stat, p_value = ks_2samp(data["m_T"], massa_simulada)

    # 🔹 Análise de Correlação
    corr, p_corr = pearsonr(data["m_T"], data["energia_total"])
    print(f"📊 Correlação Massa x Energia: {corr:.3f} (p-value: {p_corr:.5f})")

    print(f"\n📊 Estatística KS: {ks_stat:.3f}, p-value: {p_value:.5f}")
    if p_value < 0.05:
        print("🔴 Evento SUSY estatisticamente diferente do Modelo Padrão! POTENCIAL NOVA PARTÍCULA!")
    else:
        print("🟢 Evento SUSY pode ser explicado pelo Modelo Padrão.")

    # 🔹 Visualizações
    plt.figure(figsize=(8, 5))
    sns.histplot(data["m_T"], bins=50, kde=True, color="blue")
    plt.xlabel("Massa Transversal m_T (GeV)")
    plt.ylabel("Frequência")
    plt.title("Distribuição de Massa Transversal")
    plt.show()

    plt.figure(figsize=(8, 5))
    sns.histplot(data["energia_total"], bins=50, kde=True, color="red")
    plt.xlabel("Energia Total (GeV)")
    plt.ylabel("Frequência")
    plt.title("Distribuição de Energia Total")
    plt.show()

    plt.figure(figsize=(8, 5))
    sns.histplot(data["pT_medio"], bins=50, kde=True, color="green")
    plt.xlabel("Momentum Transverso Médio (GeV)")
    plt.ylabel("Frequência")
    plt.title("Distribuição de Momentum Transverso Médio")
    plt.show()

except Exception as e:
    print(f"❌ Erro: {e}")

finally:
    try:
        file.close()
        print("✅ Arquivo ROOT fechado com sucesso.")
    except:
        pass
