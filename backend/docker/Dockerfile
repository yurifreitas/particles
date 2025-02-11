# Usar a imagem oficial do Apache Spark com Java 17, Python 3 e Ubuntu
FROM apache/spark:3.5.4-scala2.12-java17-python3-ubuntu

# Definir diretório de trabalho
WORKDIR /app

# Garantir que o usuário tem permissões para instalar pacotes
USER root

# Atualizar pacotes e instalar dependências adicionais
RUN apt-get update && apt-get install -y \
    libxpm-dev \
    libx11-dev \
    libxft-dev \
    libpng-dev \
    libssl-dev \
    wget \
    unzip \
    xrootd-client \
    && rm -rf /var/lib/apt/lists/*

# Instalar bibliotecas Python
RUN pip install --no-cache-dir \
    pandas dask pyarrow numpy umap-learn hdbscan plotly dash \
    networkx fastparquet scipy seaborn scikit-learn \
    findspark pyspark uproot tqdm databricks-connect mlflow \
    awkward awkward-pandas  # <-- ADICIONADO AQUI

# Criar diretórios persistentes no volume
VOLUME ["/app/data", "/app/logs"]

# Copiar scripts e configurações
COPY scripts/ /app/scripts/
COPY spark/spark-defaults.conf /opt/spark/conf/

# Definir ponto de entrada padrão
ENTRYPOINT ["bash"]
