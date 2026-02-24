import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from config import TEST_SIZE, RANDOM_STATE
from utils.validacao import calcular_metricas

def treinar_modelo_racao(dados: pd.DataFrame):
    X = dados[['dias_cultivo', 'biomassa', 'temperatura', 'taxa_arraçoamento']]
    y = dados['consumo_diario']

    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    pipeline = Pipeline([
        ('normalizacao', StandardScaler()),
        ('regressao', LinearRegression())
    ])

    pipeline.fit(X_treino, y_treino)

    y_previsto = pipeline.predict(X_teste)
    r2, rmse = calcular_metricas(y_teste, y_previsto)

    return pipeline, r2, rmse


def prever_dias_restantes_racao(modelo, estoque_atual, dados_futuros):
    consumo_previsto = modelo.predict(dados_futuros)
    consumo_medio = consumo_previsto.mean()
    return estoque_atual / consumo_medio
