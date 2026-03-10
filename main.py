# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
import os

from utils.persistencia import carregar_modelo
from config import CAMINHO_MODELOS
from rotas import gramatura, racao

caminho_modelo_desempenho = os.path.join(CAMINHO_MODELOS, "modelo_desempenho.pkl")
caminho_modelo_racao = os.path.join(CAMINHO_MODELOS, "modelo_racao.pkl")

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(CAMINHO_MODELOS, exist_ok=True)
    
    app.state.modelos = {}
    
    try:
        app.state.modelos['desempenho'] = carregar_modelo(caminho_modelo_desempenho)
        print("Modelo de Desempenho Zootécnico carregado.")
    except Exception:
        print("Modelo de Desempenho não encontrado.")
    
    try:
        app.state.modelos['racao'] = carregar_modelo(caminho_modelo_racao)
        print("Modelo de Ração carregado.")
    except Exception:
        print("Modelo de Ração não encontrado.")
        
    yield
    app.state.modelos.clear()

app = FastAPI(
    title="API Carcinicultura",
    description="API com Regressão linear para previsão de consumo de ração E cálculo da estimativa de biomassa e FCA.",
    lifespan=lifespan
)

app.include_router(gramatura.router)
app.include_router(racao.router)

@app.get("/", summary="Raiz da API")
def read_root():
    return {"mensagem": "API Zootécnica Modular online! Acesse /docs para o Swagger."}