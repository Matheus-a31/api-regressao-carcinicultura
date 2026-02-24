import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from config import TEST_SIZE, RANDOM_STATE
from utils.validacao import calcular_metricas

def treinar_modelo_gramatura(dados: pd.DataFrame):
    X = dados[['dias_cultivo', 'temperatura', 'salinidade', 'racao']]
    y = dados['gramatura']

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


def prever_gramatura(modelo, dias, temperatura, salinidade, racao):
    entrada = pd.DataFrame([{
        'dias_cultivo': dias,
        'temperatura': temperatura,
        'salinidade': salinidade,
        'racao': racao
    }])

    return modelo.predict(entrada)[0]
