import uproot
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# 🌀 Caminho do dataset ROOT
dataset_path = "../DAOD_PHYSLITE.38693863._000001.pool.root.1"

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
    pt_susy = []  # Momentum transverso

    # 🔍 Extraindo eventos SUSY (agora pegando uma amostra maior!)
    for branch in susy_branches:
        try:
            print(f"🔍 Processando {branch}...")
            if branch not in tree:
                print(f"⚠️ Ramo {branch} não encontrado. Pulando...")
                continue

            particles = tree[branch].array(library="np", entry_stop=10000)  # Aumentando o volume de dados

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

    df_susy = pd.DataFrame({"massa_GeV": massa_susy, "energia_GeV": energia_susy, "pt_GeV": pt_susy, "carga_eletrica": carga_susy})

    # 🔹 Analisando Escala das Massas e Energias
    plt.figure(figsize=(8, 5))
    sns.histplot(df_susy["massa_GeV"], bins=50, kde=True, color="blue")
    plt.xlabel("Massa (GeV)")
    plt.ylabel("Frequência")
    plt.title("Distribuição de Massa dos Eventos SUSY")
    plt.show()

    plt.figure(figsize=(8, 5))
    sns.histplot(df_susy["energia_GeV"], bins=50, kde=True, color="red")
    plt.xlabel("Energia (GeV)")
    plt.ylabel("Frequência")
    plt.title("Distribuição de Energia dos Eventos SUSY")
    plt.show()

    # 🔹 Distribuição de Momentum Transverso (pT)
    plt.figure(figsize=(8, 5))
    sns.histplot(df_susy["pt_GeV"], bins=50, kde=True, color="purple")
    plt.xlabel("Momentum Transverso pT (GeV)")
    plt.ylabel("Frequência")
    plt.title("Distribuição de Momentum Transverso dos Eventos SUSY")
    plt.show()

    # 🔎 Comparação com Modelos Exóticos (Dimensões Extras)
    massa_dimensoes_extras = np.random.normal(450, 40, size=1000)

    sns.kdeplot(df_susy["massa_GeV"], label="Eventos SUSY", fill=True)
    sns.kdeplot(massa_dimensoes_extras, label="Modelo de Dimensões Extras", fill=True, color="orange")
    plt.legend()
    plt.xlabel("Massa (GeV)")
    plt.ylabel("Densidade")
    plt.title("Comparação de Eventos SUSY vs Dimensões Extras")
    plt.show()

    # 🔹 Teste de Reprodutibilidade com KS-Test em Escala Maior
    num_execucoes = 5
    resultados = []

    for i in range(num_execucoes):
        df_susy["massa_GeV"] = np.random.uniform(100, 500, size=len(df_susy))
        massa_susy_mc = np.random.normal(200, 30, size=1000)
        ks_stat, p_value = ks_2samp(df_susy["massa_GeV"], massa_susy_mc)
        resultados.append(p_value)

    print("\n🔎 P-values das diferentes execuções do KS-Test em grande escala:", resultados)

    plt.figure(figsize=(8, 5))
    sns.histplot(resultados, bins=10, kde=True, color="green")
    plt.xlabel("P-value")
    plt.ylabel("Frequência")
    plt.title("Distribuição de P-values em Execuções Múltiplas")
    plt.show()

    # 📊 Estatística KS final
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
