import os
import dask.dataframe as dd
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Diretório onde os arquivos Parquet estão armazenados
PROCESSED_PARQUET_DIR = "/app/data/processed_parquet_parts"


# Função para carregar os dados de forma otimizada
def load_sampled_events():
    """Carrega uma amostragem dos eventos processados para melhor performance."""
    print("📂 Carregando dados processados (AMOSTRA OTIMIZADA)...")

    # Leitura eficiente apenas das colunas necessárias
    df = dd.read_parquet(
        os.path.join(PROCESSED_PARQUET_DIR, "*.parquet"),
        columns=["U1", "U2", "U3", "cluster"]
    )

    # Amostragem aleatória para manter apenas uma fração gerenciável
    df = df.sample().compute()  # Mantém 1% dos dados, ajuste conforme necessário
    df["event_id"] = np.arange(len(df))  # Criar IDs sequenciais
    print(f"✅ {len(df)} eventos carregados (após amostragem).")

    return df

df = load_sampled_events()

# Seleção de eventos únicos otimizada para o Slider
unique_events = np.linspace(0, len(df) - 1, num=min(100, len(df))).astype(int)

# Criar aplicação Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Visualização Interativa - Linha do Tempo 3D"),

    # Armazena os dados carregados para evitar recarregar a cada atualização
    dcc.Store(id="stored-data", data=df.to_dict(orient="list")),

    dcc.Graph(id="3d-scatter"),

    html.Label("Selecione o Evento:"),
    dcc.Slider(
        id="event-slider",
        min=int(unique_events[0]),
        max=int(unique_events[-1]),
        value=int(unique_events[0]),
        marks={int(i): str(i) for i in unique_events[::max(1, len(unique_events) // 10)]},
        step=1
    )
])

@app.callback(
    Output("3d-scatter", "figure"),
    [Input("event-slider", "value")],
    [dash.dependencies.State("stored-data", "data")]
)
def update_figure(selected_event, stored_data):
    """Atualiza a visualização 3D conforme o evento selecionado na linha do tempo."""
    if not stored_data:
        return go.Figure()

    # Converter para DataFrame Pandas
    filtered_df = pd.DataFrame(stored_data)
    
    # Filtrar até o evento selecionado
    filtered_df = filtered_df[filtered_df["event_id"] <= selected_event]

    fig = go.Figure()

    fig.add_trace(go.Scatter3d(
        x=filtered_df['U1'],
        y=filtered_df['U2'],
        z=filtered_df['U3'],
        mode='markers',
        marker=dict(size=3, color=filtered_df['cluster'], colorscale='Rainbow', opacity=0.7),
        name="Eventos"
    ))

    fig.update_layout(title=f"Eventos até o Tempo {selected_event}",
                      scene=dict(xaxis_title="U1", yaxis_title="U2", zaxis_title="U3"),
                      transition_duration=500)

    return fig

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)
