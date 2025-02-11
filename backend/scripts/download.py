from pyspark.sql import SparkSession
import os
import subprocess
import json

# Criar sessão Spark
spark = SparkSession.builder.appName("CERNDownloader").getOrCreate()
sc = spark.sparkContext

INPUT_DIR = "/app/data/cern_raw"
os.makedirs(INPUT_DIR, exist_ok=True)

CHECKPOINT_FILE = "/app/logs/parquet_checkpoint.json"

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return json.load(f)
    return {}

def save_checkpoint(checkpoint):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(checkpoint, f, indent=4)

checkpoint = load_checkpoint()

urls = [
    f"root://eospublic.cern.ch//eos/opendata/atlas/rucio/data15_hi/DAOD_HION14.41691899._{i:06d}.pool.root.1"
    for i in range(1, 38)
]

def download_file(url):
    filename = os.path.join(INPUT_DIR, url.split("/")[-1])
    if os.path.exists(filename):
        print(f"Arquivo já existe: {filename} (Pulando)")
        return True

    command = ["xrdcp", url, filename]
    try:
        print(f"Baixando: {filename}")
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"✅ Download concluído: {filename}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao baixar: {url}: {e.stderr}")
        return False

# Criar RDD e executar os downloads em paralelo
rdd = sc.parallelize(urls, numSlices=10)

download_results = rdd.map(download_file).collect()

all_downloads_successful = all(download_results)

if all_downloads_successful:
    print("🎉 Todos os downloads foram concluídos com sucesso!")

    # Seu código para processar os arquivos baixados AQUI
    # Exemplo:
    for filename in os.listdir(INPUT_DIR):
       print(f"Arquivo: {filename}")

    # Próximo passo do seu pipeline
    # ... (seu código para processar os arquivos, gerar outros arquivos, etc.)

else:
    print("❌ Pelo menos um download falhou. Verifique os logs de erro.")
    # Lógica para lidar com falhas (ex: tentar novamente, notificar, etc.)

spark.stop()

# Exemplo de código para o "próximo passo" (substitua por sua lógica):
if all_downloads_successful:
    # Exemplo: contar o número de linhas em cada arquivo Parquet
    parquet_files = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.endswith(".parquet")]
    for file in parquet_files:
        try:
            df = spark.read.parquet(file)
            row_count = df.count()
            print(f"Arquivo Parquet: {file}, Linhas: {row_count}")
        except Exception as e:
            print(f"Erro ao processar arquivo Parquet: {file}: {e}")