import pandas as pd
from modelos.racao import treinar_modelo_racao, prever_dias_restantes_racao

dados = pd.DataFrame({
    'dias_cultivo': [10, 20, 30, 40, 50, 60],
    'biomassa': [50, 80, 120, 160, 200, 240],
    'temperatura': [28, 29, 29, 30, 30, 31],
    'taxa_arraçoamento': [0.04, 0.05, 0.06, 0.07, 0.08, 0.08],
    'consumo_diario': [2.0, 3.5, 5.2, 7.1, 9.0, 11.5]
})

modelo, r2, rmse = treinar_modelo_racao(dados)

print(f"R² consumo: {r2:.3f}")
print(f"RMSE consumo: {rmse:.3f}")
