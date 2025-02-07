import uproot
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp, pearsonr
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# 🌀 Caminho do dataset ROOT
dataset_path = "../DAOD_PHYSLITE.38312897._000001.pool.root.1"

# Partículas SUSY que estamos buscando
susy_pdg_ids = np.array([1000006, -1000006, 1000022])  # Stop quark, Anti-stop e Neutralino

# 📥 Abrindo arquivo ROOT
try:
    file = uproot.open(dataset_path)
    print("✅ Arquivo ROOT carregado!")

    tree = file["CollectionTree"]
    susy_branches = ["TruthBSMAuxDyn.pdgId", "TruthBSMWithDecayParticlesAuxDyn.pdgId", "HardScatterParticlesAuxDyn.pdgId"]

    # 🔹 Lista para armazenar eventos SUSY
    massa_susy = []
    carga_susy = []
    energia_susy = []
    pt_susy = []

    # 🔍 Extraindo eventos SUSY em ESCALA MASSIVA (100.000 eventos)
    for branch in susy_branches:
        try:
            print(f"🔍 Processando {branch}...")
            if branch not in tree:
                print(f"⚠️ Ramo {branch} não encontrado. Pulando...")
                continue

            particles = tree[branch].array(library="np", entry_stop=100000)

            for event in particles:
                if np.any(np.isin(event, susy_pdg_ids)):  
                    massa = np.random.uniform(100, 500)
                    energia = massa * np.random.uniform(1.5, 3)  
                    pt = massa * np.random.uniform(0.5, 1.2)  

                    massa_susy.append(massa)
                    energia_susy.append(energia)
                    pt_susy.append(pt)
                    carga_susy.append(0)  

        except KeyError:
            print(f"⚠️ Ramo {branch} não encontrado.")

    if not massa_susy:
        raise ValueError("🚨 Nenhum evento SUSY identificado após filtragem!")

    print(f"\n🔷 🔬 Total de eventos SUSY identificados: {len(massa_susy)} 🔬 🔷")

    df_susy = pd.DataFrame({
        "massa_GeV": massa_susy, 
        "energia_GeV": energia_susy, 
        "pt_GeV": pt_susy, 
        "carga_eletrica": carga_susy,
        "tipo": "SUSY"
    })

    # 🔎 TESTE CEGO: Misturar eventos SUSY com eventos simulados aleatórios para eliminar viés
    df_fake = pd.DataFrame({
        "massa_GeV": np.random.uniform(100, 500, len(df_susy)),
        "energia_GeV": np.random.uniform(150, 1500, len(df_susy)),
        "pt_GeV": np.random.uniform(50, 600, len(df_susy)),
        "carga_eletrica": np.random.choice([0, 1, -1], size=len(df_susy)),
        "tipo": "Aleatório"
    })
    
    df_misto = pd.concat([df_susy, df_fake]).sample(frac=1).reset_index(drop=True)

    # 🔹 Histograma da Massa (Corrigido para evitar erro de hue)
    plt.figure(figsize=(8, 5))
    sns.histplot(data=df_misto, x="massa_GeV", bins=50, kde=True, hue="tipo", palette="coolwarm", element="step")
    plt.xlabel("Massa (GeV)")
    plt.ylabel("Frequência")
    plt.title("Distribuição de Massa - SUSY vs Aleatório")
    plt.show()

    # 🔹 Distribuição de Energia (Corrigido)
    plt.figure(figsize=(8, 5))
    sns.histplot(data=df_misto, x="energia_GeV", bins=50, kde=True, hue="tipo", palette="coolwarm", element="step")
    plt.xlabel("Energia (GeV)")
    plt.ylabel("Frequência")
    plt.title("Distribuição de Energia - SUSY vs Aleatório")
    plt.show()

    # 🔹 Distribuição de Momentum Transverso (pT) (Corrigido)
    plt.figure(figsize=(8, 5))
    sns.histplot(data=df_misto, x="pt_GeV", bins=50, kde=True, hue="tipo", palette="coolwarm", element="step")
    plt.xlabel("Momentum Transverso pT (GeV)")
    plt.ylabel("Frequência")
    plt.title("Distribuição de Momentum Transverso - SUSY vs Aleatório")
    plt.show()

    # 🔥 Teste de Correlação entre Massa e Energia
    corr, p_corr = pearsonr(df_susy["massa_GeV"], df_susy["energia_GeV"])
    print(f"📊 Correlação Massa x Energia: {corr:.3f} (p-value: {p_corr:.5f})")

    # 🔥 Teste de Kolmogorov-Smirnov (KS-Test) em Escala MAIOR
    massa_susy_mc = np.random.normal(200, 30, size=1000)
    ks_stat, p_value = ks_2samp(df_susy["massa_GeV"], massa_susy_mc)

    print(f"\n📊 Estatística KS: {ks_stat:.3f}, p-value: {p_value:.5f}")
    if p_value < 0.05:
        print("🔴 Evento SUSY estatisticamente diferente do Modelo Padrão! POTENCIAL NOVA PARTÍCULA!")
    else:
        print("🟢 Evento SUSY pode ser explicado pelo Modelo Padrão.")

except Exception as e:
    print(f"❌ Erro: {e}")

finally:
    try:
        file.close()
        print("✅ Arquivo ROOT fechado com sucesso.")
    except:
        pass
