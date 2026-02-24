import joblib
import os

def salvar_modelo(modelo, caminho):
    pasta = os.path.dirname(caminho)
    if pasta:
        os.makedirs(pasta, exist_ok=True)
    joblib.dump(modelo, caminho)


def carregar_modelo(caminho):
    return joblib.load(caminho)
