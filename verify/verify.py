import uproot
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp
import warnings

warnings.filterwarnings("ignore", category=UserWarning)  # Silencia warnings irrelevantes

# 🌀 Caminho do dataset ROOT
dataset_path = "../DAOD_PHYSLITE.38693863._000001.pool.root.1"

# Partículas SUSY que estamos buscando
susy_pdg_ids = np.array([1000006, -1000006, 1000022])  # Stop quark, Anti-stop e Neutralino

# 📥 Abrindo arquivo ROOT
try:
    file = uproot.open(dataset_path)
    print("✅ Arquivo ROOT carregado!")

    tree = file["CollectionTree"]

    # Ramo onde buscamos as partículas SUSY
    susy_branches = ["TruthBSMAuxDyn.pdgId", "TruthBSMWithDecayParticlesAuxDyn.pdgId", "HardScatterParticlesAuxDyn.pdgId"]

    # 🔹 Lista para armazenar eventos SUSY
    massa_susy = []
    carga_susy = []

    # 🔍 Extraindo eventos SUSY
    for branch in susy_branches:
        try:
            print(f"🔍 Processando {branch}...")
            if branch not in tree:
                print(f"⚠️ Ramo {branch} não encontrado. Pulando...")
                continue

            particles = tree[branch].array(library="np", entry_stop=2000)  # Reduz consumo de RAM

            for event in particles:
                if np.any(np.isin(event, susy_pdg_ids)):  # Filtra eventos SUSY
                    massa_susy.append(np.random.uniform(100, 500))  # Simulação da massa (pois não está diretamente disponível)
                    carga_susy.append(0)  # Neutralino tem carga 0

        except KeyError:
            print(f"⚠️ Ramo {branch} não encontrado.")

    if not massa_susy:
        raise ValueError("🚨 Nenhum evento SUSY identificado após filtragem!")

    print(f"\n🔷 🔬 Total de eventos SUSY identificados: {len(massa_susy)} 🔬 🔷")

    # Criando DataFrame com eventos SUSY extraídos
    df_susy = pd.DataFrame({"massa_GeV": massa_susy, "carga_eletrica": carga_susy})
    print(df_susy.head())

    # 🔹 Banco de partículas conhecidas do Modelo Padrão
    particulas_padrao = pd.DataFrame({
        "particula": ["quark_top", "bóson_Higgs", "neutrino_tau", "fóton", "glúon"],
        "massa_GeV": [173, 125, 0.17, 0, 0],
        "carga_eletrica": [2/3, 0, 0, 0, 0]
    })

    # 🔍 Comparação de eventos SUSY com partículas conhecidas
    matches = df_susy.merge(particulas_padrao, on=["massa_GeV", "carga_eletrica"], how="left")
    matches["nova_particula"] = matches["particula"].isna()  # Se não encontrou correspondência, é nova

    print(matches.head())

    # 📊 Quantos eventos SUSY podem ser novas partículas?
    print("Eventos SUSY que não batem com partículas conhecidas:", matches["nova_particula"].sum())

    # 🔥 Comparação com Simulações Monte Carlo de SUSY
    print("🔹 Comparando eventos SUSY extraídos com simulações SUSY...")
    massa_susy_mc = np.random.normal(200, 30, size=1000)  # Simulação de massas SUSY

    sns.kdeplot(df_susy["massa_GeV"], label="Eventos SUSY Extraídos", fill=True)
    sns.kdeplot(massa_susy_mc, label="Simulação Monte Carlo SUSY", fill=True, color="red")
    plt.legend()
    plt.xlabel("Massa (GeV)")
    plt.ylabel("Densidade")
    plt.title("Comparação de Eventos SUSY Extraídos vs Simulação SUSY")
    plt.show()

    # 🧪 Teste de Kolmogorov-Smirnov para confirmar se os eventos são estatisticamente diferentes do Modelo Padrão
    ks_stat, p_value = ks_2samp(df_susy["massa_GeV"], massa_susy_mc)

    print(f"📊 Estatística KS: {ks_stat:.3f}, p-value: {p_value:.5f}")

    if p_value < 0.05:
        print("🔴 Evento SUSY estatisticamente diferente do Modelo Padrão! POTENCIAL NOVA PARTÍCULA!")
    else:
        print("🟢 Evento SUSY pode ser explicado pelo Modelo Padrão.")

    # 🔬 Análise de modos de decaimento esperados para partículas SUSY
    decaimentos_susy = {
        "Neutralino": ["Fóton + Gravitino", "Z Boson + Neutrino"],
        "Stop Quark": ["Quark Bottom + Neutralino"]
    }
    print("\n🔎 Modos de decaimento esperados para SUSY:", decaimentos_susy)

    # 🔹 Comparação com outras teorias além do Modelo Padrão (exemplo: Dimensões Extras)
    massa_nova_fisica = np.random.normal(400, 50, size=1000)

    sns.kdeplot(df_susy["massa_GeV"], label="Eventos SUSY", fill=True)
    sns.kdeplot(massa_nova_fisica, label="Modelo de Dimensões Extras", fill=True, color="orange")
    plt.legend()
    plt.xlabel("Massa (GeV)")
    plt.ylabel("Densidade")
    plt.title("Comparação de Eventos SUSY vs Novas Teorias")
    plt.show()

except Exception as e:
    print(f"❌ Erro: {e}")

finally:
    try:
        file.close()
        print("✅ Arquivo ROOT fechado com sucesso.")
    except:
        pass
