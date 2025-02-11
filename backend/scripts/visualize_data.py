import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# ***CONFIGURAÇÕES***
PROCESSED_PARQUET_DIR = "/app/data/cern_parquet"  # Ajuste para seu diretório Parquet

# ***FUNÇÃO PARA CARREGAR OS DADOS***
def load_data():
    """Carrega dados, com amostragem e tratamento de erros."""
    print("Carregando dados...")

    try:
        df = pd.read_parquet(os.path.join(PROCESSED_PARQUET_DIR, "*.parquet"))

        # Criação do event_id
        df["event_id"] = np.arange(len(df))

        print(f"Dados carregados. Shape: {df.shape}")

        return df

    except FileNotFoundError:
        print(f"Erro: Arquivos Parquet não encontrados em {PROCESSED_PARQUET_DIR}")
        return pd.DataFrame({'U1': [], 'U2': [], 'U3': [], 'cluster': [], 'event_id': []})  # DataFrame vazio
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return pd.DataFrame({'U1': [], 'U2': [], 'U3': [], 'cluster': [], 'event_id': []})  # DataFrame vazio


# ***CARREGAMENTO INICIAL DOS DADOS***
df = load_data()

if df.empty:
    print("Erro: DataFrame vazio. Verifique os arquivos Parquet e o diretório.")
    exit()

unique_clusters = df['cluster'].unique().tolist()
min_event_id = int(df['event_id'].min())
max_event_id = int(df['event_id'].max())


# ***CRIAÇÃO DO APP DASH***
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Visualização Interativa - Linha do Tempo 3D"),
    dcc.Graph(id="3d-scatter"),
    html.Label("Selecione o(s) Cluster(es):"),
    dcc.Dropdown(
        id="cluster-dropdown",
        options=[{'label': str(cluster), 'value': cluster} for cluster in unique_clusters],
        value=unique_clusters,  # Todos os clusters selecionados inicialmente
        multi=True
    ),
    html.Label("Selecione o Evento:"),
    dcc.Slider(
        id="event-slider",
        min=min_event_id,
        max=max_event_id,
        value=min_event_id,  # Valor inicial: o primeiro evento
        marks={int(i): str(i) for i in np.linspace(min_event_id, max_event_id, num=min(100, max_event_id - min_event_id + 1)).astype(int)},  # Ajuste marks
        step=1
    )
])


# ***CALLBACK***
@app.callback(
    Output("3d-scatter", "figure"),
    [Input("event-slider", "value"),
     Input("cluster-dropdown", "value")]
)
def update_figure(selected_event, selected_clusters):
    """Atualiza a visualização 3D."""

    df_filtered = df.copy()  # Cria uma cópia para não alterar o dataframe original

    if selected_clusters:
        df_filtered = df_filtered[df_filtered['cluster'].isin(selected_clusters)]

    df_filtered = df_filtered[df_filtered["event_id"] <= selected_event]


    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=df_filtered['U1'],
        y=df_filtered['U2'],
        z=df_filtered['U3'],
        mode='markers',
        marker=dict(size=3, color=df_filtered['cluster'], colorscale='Rainbow', opacity=0.7),
        name="Eventos"
    ))

    fig.update_layout(title=f"Eventos até o Tempo {selected_event}",
                      scene=dict(xaxis_title="U1", yaxis_title="U2", zaxis_title="U3"),
                      transition_duration=500)

    return fig


# ***EXECUÇÃO DO APP***
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)