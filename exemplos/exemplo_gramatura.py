import sys
import os
import pandas as pd

caminho_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, caminho_raiz)

from modelos.gramatura import treinar_modelo_gramatura, prever_gramatura
from utils.persistencia import salvar_modelo, carregar_modelo
from config import CAMINHO_MODELOS

dados = pd.DataFrame({
    'dias_cultivo': [10, 20, 30, 40, 50, 60, 70],
    'temperatura': [28, 29, 29, 30, 30, 31, 31],
    'salinidade': [25, 26, 26, 27, 27, 28, 28],
    'racao': [1.2, 1.5, 1.8, 2.1, 2.5, 2.9, 3.2],
    'gramatura': [2.0, 4.5, 6.9, 9.1, 11.8, 14.3, 17.0]
})

modelo, r2, rmse = treinar_modelo_gramatura(dados)

print(f"R²: {r2:.3f}")
print(f"RMSE: {rmse:.3f}")

os.makedirs(CAMINHO_MODELOS, exist_ok=True)
caminho = os.path.join(CAMINHO_MODELOS, "modelo_gramatura.pkl")

salvar_modelo(modelo, caminho)

modelo_carregado = carregar_modelo(caminho)
g = prever_gramatura(modelo_carregado, 80, 31, 28, 3.5)

print(f"Gramatura prevista: {g:.2f} g")
print("Modelo treinado e salvo com sucesso na pasta modelos_salvos!")