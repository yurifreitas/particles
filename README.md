# 📄 Análise Avançada de Eventos de Colisão do ATLAS (CERN)

## 🚀 Descrição do Projeto
Este projeto realiza uma análise avançada de dados reais de colisões do experimento **ATLAS** no **LHC (CERN)**, utilizando métodos estatísticos rigorosos e visualizações interativas para identificar padrões incomuns que podem sugerir evidências de **supersimetria (SUSY)** ou novas partículas.

---

## 📌 Principais Objetivos

✔️ Carregar e processar eventos de colisão reais diretamente de arquivos **ROOT** do CERN.  
✔️ Aplicar estatísticas robustas, incluindo **KS-Test** e **Anderson-Darling Test**, para verificar anomalias.  
✔️ Utilizar técnicas avançadas de redução de dimensionalidade, como **t-SNE**, **UMAP** e **Isomap**.  
✔️ Gerar **visualizações interativas** e **multidimensionais**, explorando estruturas ocultas nos dados.  
✔️ Investigar padrões incomuns que podem ser indicativos de fenômenos ainda não explicados pelo **Modelo Padrão**.  

---

## 🛠 Tecnologias Utilizadas

🔹 **Python (3.11+)**  
🔹 **UPROOT** (Leitura de arquivos ROOT)  
🔹 **NumPy & Pandas** (Manipulação de dados)  
🔹 **SciPy** (Estatísticas avançadas)  
🔹 **Seaborn & Matplotlib** (Gráficos tradicionais)  
🔹 **Plotly** (Visualizações interativas)  
🔹 **Scikit-Learn** (t-SNE, Isomap, PCA)  
🔹 **UMAP** (Mapeamento não-linear)  

---

## 📊 Fluxo da Análise

1️⃣ **Carregar dados ROOT** 📥  
2️⃣ **Filtrar eventos físicos relevantes** ⚛️  
3️⃣ **Remover ruído e tratar dados ausentes** 🧹  
4️⃣ **Calcular estatísticas de anomalias** 📈  
5️⃣ **Aplicar projeções não-lineares** (t-SNE, UMAP, Isomap) 🌀  
6️⃣ **Gerar visualizações interativas** 🎨  
7️⃣ **Interpretar padrões ocultos e anomalias** 🔍  

---

## 🔬 Métricas Estatísticas Utilizadas

📌 **Correlação pT x Energia** (Correlação entre Momentum Transverso e Energia Total)  
📌 **Teste de Kolmogorov-Smirnov (KS-Test)** (Comparação entre dados reais e simulações do Modelo Padrão)  
📌 **Teste de Anderson-Darling (AD-Test)** (Verificação de distribuição estatística para detecção de anomalias)  

---

## 🎨 Visualizações Criadas

✅ **t-SNE (3D)** - Para agrupar partículas semelhantes em um espaço tridimensional.  
✅ **UMAP (3D)** - Técnica de projeção não-linear que preserva topologias dos dados.  
✅ **Isomap (3D)** - Redução de dimensionalidade baseada em distâncias geodésicas.  
✅ **Mapa de calor de correlações** - Para identificar dependências entre variáveis.  
✅ **Gráficos de dispersão interativos** - Para explorar clusters e padrões incomuns.  

---

## 🚀 Como Rodar o Projeto

### 1️⃣ Instale as dependências:

```bash
pip install -r requirements.txt

## 🔗 Referências

- [CERN Open Data Portal](https://opendata.cern.ch/)
- [Dataset do ATLAS no CERN](https://opendata.cern.ch/record/80036)

## 🎯 Próximos Passos

- 🔹 Explorar eventos de colisão **Pb-Pb** para testar se padrões se repetem.
- 🔹 Incorporar **redes neurais** para identificar anomalias mais sutis.



### Melhorias Aplicadas:
- Estruturação e organização do texto com **quebra de seções**.
- Correção da formatação Markdown para garantir melhor **visualização e legibilidade**.
- Adição de **listas e espaçamentos adequados** para melhor leitura.
- Uso de **ícones e emojis** para uma apresentação mais visual e dinâmica.

Agora seu README está pronto no **padrão profissional**! 🚀
