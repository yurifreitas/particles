
# Projeto de Análise de Dados do CERN com Spark, Dask, UMAP, HDBSCAN e Dash

Este projeto demonstra um pipeline completo para análise de dados do CERN, desde o download dos dados brutos, passando pela conversão para o formato Parquet, processamento com Dask, redução de dimensionalidade com UMAP, clustering com HDBSCAN, geração de grafos fractais e, finalmente, visualização interativa com Dash. O projeto utiliza o Apache Spark para o download paralelo dos dados e o Dask para o processamento eficiente de grandes conjuntos de dados.

## Arquitetura

O projeto é composto por scripts Python que executam as seguintes etapas:

1.  **Download:** `download.py` baixa os arquivos ROOT brutos do CERN usando `xrdcp` e Spark para paralelização.
2.  **Conversão:** `converting_parquet.py` converte os arquivos ROOT para o formato Parquet usando `uproot` e `pyarrow`.
3.  **Processamento:** `processed_parquet.py` carrega os arquivos Parquet com Dask, aplica redução de dimensionalidade com UMAP, clustering com HDBSCAN e gera conexões fractais complexas.
4.  **Visualização:** `visualize_data.py` cria um dashboard interativo com Dash para explorar os dados processados, permitindo selecionar clusters, eventos e visualizar a distribuição 3D dos dados.

## Dependências

Certifique-se de ter as seguintes bibliotecas Python instaladas:

*   `pyspark`
*   `uproot`
*   `pyarrow`
*   `pandas`
*   `numpy`
*   `dask`
*   `scikit-learn`
*   `umap-learn`
*   `hdbscan`
*   `networkx`
*   `plotly`
*   `dash`

Você pode instalá-las usando `pip`:

```bash
pip install pyspark uproot pyarrow pandas numpy dask scikit-learn umap-learn hdbscan networkx plotly dash
```

## Configuração

1.  **Diretórios:**
    *   `INPUT_DIR`: `/app/data/cern_raw` (Diretório para arquivos ROOT brutos)
    *   `OUTPUT_DIR`: `/app/data/parquet` (Diretório para arquivos Parquet convertidos)
    *   `PROCESSED_PARQUET_DIR`: `/app/data/processed_parquet_parts` (Diretório para arquivos Parquet processados)
    *   `CHECKPOINT_FILE`: `/app/logs/parquet_checkpoint.json` (Arquivo de checkpoint para controle de progresso)

2.  **Variáveis:**
    Ajuste as variáveis dentro dos scripts Python conforme necessário, como caminhos de arquivos, parâmetros para UMAP e HDBSCAN, etc.

## Uso

1.  **Download:**

```bash
python download.py
```

2.  **Conversão:**

```bash
python converting_parquet.py
```

3.  **Processamento:**

```bash
python processed_parquet.py
```

4.  **Visualização:**

```bash
python visualize_data.py
```

Abra o seu navegador e acesse `http://127.0.0.1:8050/` para interagir com o dashboard.

## Descrição dos Scripts

*   **`download.py`:** Baixa arquivos ROOT do CERN usando `xrdcp` e Spark. Utiliza um arquivo de checkpoint para evitar downloads repetidos.
*   **`converting_parquet.py`:** Converte arquivos ROOT para Parquet, lendo os dados com `uproot` e salvando-os com `pyarrow`.
*   **`processed_parquet.py`:**
    *   Carrega arquivos Parquet com Dask.
    *   Aplica UMAP para reduzir a dimensionalidade dos dados para 3 componentes (U1, U2, U3).
    *   Realiza o clustering com HDBSCAN para identificar grupos de eventos.
    *   Gera conexões fractais entre os eventos para simular relações complexas.
    *   Salva os dados processados em formato Parquet.
*   **`visualize_data.py`:** Cria um dashboard interativo com Dash, permitindo:
    *   Selecionar clusters para visualização.
    *   Selecionar um evento específico para exibir os dados até aquele ponto.
    *   Visualizar os dados em um gráfico 3D interativo.

## Observações

*   Os arquivos de checkpoint são usados para acompanhar o progresso e evitar reprocessamento de dados.
*   Ajuste os parâmetros de UMAP e HDBSCAN de acordo com as características dos seus dados.
*   O dashboard Dash permite explorar os dados de forma interativa, facilitando a identificação de padrões e insights.
*   Este README fornece uma visão geral do projeto. Consulte os scripts individuais para detalhes de implementação.

## Próximos Passos

*   Explorar diferentes parâmetros para UMAP e HDBSCAN.
*   Adicionar mais funcionalidades ao dashboard Dash, como filtros, gráficos adicionais, etc.
*   Integrar o pipeline com outras ferramentas de análise de dados.