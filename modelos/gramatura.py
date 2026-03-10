import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from config import TEST_SIZE, RANDOM_STATE
from utils.validacao import calcular_metricas

def treinar_modelo_gramatura(dados: pd.DataFrame):
    # Agora a IA olha para TODAS as variáveis de causa
    features = ['dias_cultivo', 'temperatura', 'salinidade', 'densidade', 'sobrevivencia_est', 'racao_acumulada']
    X = dados[features]
    y = dados['gramatura'] # Efeito (o que queremos prever)

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