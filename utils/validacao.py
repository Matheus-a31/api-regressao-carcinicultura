import numpy as np
from sklearn.metrics import r2_score, mean_squared_error

def calcular_metricas(y_real, y_previsto):
    r2 = r2_score(y_real, y_previsto)
    rmse = np.sqrt(mean_squared_error(y_real, y_previsto))
    return r2, rmse
