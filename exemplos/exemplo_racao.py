import sys
import os
import joblib
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modelos.racao import treinar_modelo_racao, prever_dias_restantes_racao

dados = pd.DataFrame({
    'dias_cultivo': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
    'biomassa': [50, 80, 120, 160, 200, 240, 280, 320, 360, 400],
    'temperatura': [28, 29, 29, 30, 30, 31, 31, 30, 29, 28],
    'taxa_arraçoamento': [0.04, 0.05, 0.06, 0.07, 0.08, 0.08, 0.07, 0.06, 0.05, 0.04],
    'consumo_diario': [2.0, 3.5, 5.2, 7.1, 9.0, 11.5, 13.0, 14.2, 15.1, 15.8]
})

print("Treinando o modelo...")
modelo, r2, rmse = treinar_modelo_racao(dados)

print(f"R² consumo: {r2:.3f}")
print(f"RMSE consumo: {rmse:.3f}\n")

pasta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
pasta_modelos = os.path.join(pasta_raiz, 'modelos_salvos')

os.makedirs(pasta_modelos, exist_ok=True) 

caminho_arquivo = os.path.join(pasta_modelos, 'modelo_racao.pkl')
joblib.dump(modelo, caminho_arquivo)
print(f"Modelo salvo com sucesso em: {caminho_arquivo}\n")

estoque_atual = 50.0

dados_futuros = pd.DataFrame({
    'dias_cultivo': [110, 120, 130],
    'biomassa': [440, 480, 520],
    'temperatura': [28, 28, 29],
    'taxa_arraçoamento': [0.03, 0.03, 0.03]
})

print("Calculando previsão de estoque...")
dias_restantes = prever_dias_restantes_racao(modelo, estoque_atual, dados_futuros)

print(f"Com um estoque de {estoque_atual}kg, a ração vai durar aproximadamente {dias_restantes:.1f} dias.")