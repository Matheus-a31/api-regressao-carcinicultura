from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import pandas as pd
import os
import uuid
from contextlib import asynccontextmanager

from utils.persistencia import carregar_modelo, salvar_modelo
from modelos.gramatura import prever_gramatura, treinar_modelo_gramatura
from modelos.racao import prever_dias_restantes_racao, treinar_modelo_racao
from config import CAMINHO_MODELOS

from database import get_db, PrevisaoDB

caminho_modelo_gramatura = os.path.join(CAMINHO_MODELOS, "modelo_gramatura.pkl")
caminho_modelo_racao = os.path.join(CAMINHO_MODELOS, "modelo_racao.pkl")

modelos = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(CAMINHO_MODELOS, exist_ok=True)
    try:
        modelos['gramatura'] = carregar_modelo(caminho_modelo_gramatura)
        print("Modelo de gramatura carregado na memória.")
    except Exception as e:
        print(f"Aviso: Modelo de gramatura não encontrado ou erro ao carregar: {str(e)}")
    
    try:
        modelos['racao'] = carregar_modelo(caminho_modelo_racao)
        print("Modelo de ração carregado na memória.")
    except Exception as e:
        print(f"Aviso: Modelo de ração não encontrado ou erro ao carregar: {str(e)}")
        
    yield
    modelos.clear()
    print("Modelos descarregados.")

app = FastAPI(
    title="API de Regressão linear - Carcinicultura",
    description="API preditiva conectada ao PostgreSQL para salvar histórico. Com debug de erros ativado.",
    lifespan=lifespan
)

# --- MODELOS PYDANTIC ---
class GramaturaRequest(BaseModel):
    dias_cultivo: int
    temperatura: float
    salinidade: float
    racao: float

class DadosTreinamentoGramatura(BaseModel):
    dias_cultivo: int
    temperatura: float
    salinidade: float
    racao: float
    gramatura: float

class RetreinarGramaturaRequest(BaseModel):
    historico: List[DadosTreinamentoGramatura]

class CondicaoFutura(BaseModel):
    dias_cultivo: int
    biomassa: float
    temperatura: float
    taxa_arraçoamento: float

class RacaoRequest(BaseModel):
    estoque_atual: float
    dados_futuros: List[CondicaoFutura]

class DadosTreinamentoRacao(BaseModel):
    dias_cultivo: int
    biomassa: float
    temperatura: float
    taxa_arraçoamento: float
    consumo_diario: float

class RetreinarRacaoRequest(BaseModel):
    historico: List[DadosTreinamentoRacao]

def extrair_dicionario(modelo_pydantic):
    if hasattr(modelo_pydantic, 'model_dump'):
        return modelo_pydantic.model_dump()
    return modelo_pydantic.dict()


@app.get("/", summary="Raiz da API")
def read_root():
    return {"mensagem": "API de regressão para Carcinicultura. Acesse a documentação em /docs"}


@app.post("/prever/gramatura", summary="Gerar e salvar previsão de gramatura no Neon")
def criar_previsao_gramatura(dados: GramaturaRequest, db: Session = Depends(get_db)):
    if 'gramatura' not in modelos:
        raise HTTPException(status_code=503, detail="Modelo de gramatura indisponível no servidor.")
    
    try:
        previsao = prever_gramatura(
            modelos['gramatura'], 
            dados.dias_cultivo, dados.temperatura, dados.salinidade, dados.racao
        )
        
        id_previsao = str(uuid.uuid4())
        parametros = extrair_dicionario(dados)
        
        novo_registro = PrevisaoDB(
            id=id_previsao,
            tipo="gramatura",
            parametros_entrada=parametros, 
            resultado_estimado=round(previsao, 2)
        )
        
        db.add(novo_registro)
        db.commit()
        db.refresh(novo_registro)
        
        return {
            "mensagem": "Previsão salva no banco com sucesso!", 
            "id": novo_registro.id, 
            "resultado_g": novo_registro.resultado_estimado
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro interno detalhado: {str(e)}")

@app.get("/prever/gramatura/{id_previsao}", summary="Buscar previsão de gramatura no Neon")
def buscar_previsao_gramatura(id_previsao: str, db: Session = Depends(get_db)):
    try:
        registro = db.query(PrevisaoDB).filter(PrevisaoDB.id == id_previsao, PrevisaoDB.tipo == "gramatura").first()
        
        if not registro:
            raise HTTPException(status_code=404, detail="Previsão não encontrada no banco.")
        
        return {
            "id": registro.id,
            "parametros": registro.parametros_entrada,
            "resultado_g": registro.resultado_estimado
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao buscar no banco: {str(e)}")

@app.post("/retreinar/gramatura", summary="Retreinar modelo de gramatura")
def retreinar_gramatura(dados: RetreinarGramaturaRequest):
    try:
        df_novos_dados = pd.DataFrame([extrair_dicionario(item) for item in dados.historico])
        if len(df_novos_dados) < 5:
            raise HTTPException(status_code=400, detail="Envie pelo menos 5 registros.")

        novo_modelo, r2, rmse = treinar_modelo_gramatura(df_novos_dados)
        salvar_modelo(novo_modelo, caminho_modelo_gramatura)
        modelos['gramatura'] = novo_modelo
        
        return {"mensagem": "Modelo de gramatura atualizado!", "r2": round(r2, 3), "rmse": round(rmse, 3)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao retreinar: {str(e)}")


@app.post("/prever/racao", summary="Gerar e salvar previsão de ração no Neon")
def criar_previsao_racao(dados: RacaoRequest, db: Session = Depends(get_db)):
    if 'racao' not in modelos:
        raise HTTPException(status_code=503, detail="Modelo de ração indisponível no servidor.")
    
    try:
        df_futuro = pd.DataFrame([extrair_dicionario(item) for item in dados.dados_futuros])
        dias_restantes = prever_dias_restantes_racao(modelos['racao'], dados.estoque_atual, df_futuro)
        
        id_previsao = str(uuid.uuid4())
        parametros = extrair_dicionario(dados)
        
        novo_registro = PrevisaoDB(
            id=id_previsao,
            tipo="racao",
            parametros_entrada=parametros, 
            resultado_estimado=round(dias_restantes, 1)
        )
        
        db.add(novo_registro)
        db.commit()
        db.refresh(novo_registro)
        
        return {
            "mensagem": "Previsão salva no banco com sucesso!", 
            "id": novo_registro.id, 
            "dias_restantes": novo_registro.resultado_estimado
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro interno detalhado: {str(e)}")

@app.get("/prever/racao/{id_previsao}", summary="Buscar previsão de ração no Neon")
def buscar_previsao_racao(id_previsao: str, db: Session = Depends(get_db)):
    try:
        registro = db.query(PrevisaoDB).filter(PrevisaoDB.id == id_previsao, PrevisaoDB.tipo == "racao").first()
        
        if not registro:
            raise HTTPException(status_code=404, detail="Previsão não encontrada no banco.")
        
        return {
            "id": registro.id,
            "parametros": registro.parametros_entrada,
            "dias_restantes": registro.resultado_estimado
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao buscar no banco: {str(e)}")

@app.post("/retreinar/racao", summary="Retreinar modelo de ração")
def retreinar_racao(dados: RetreinarRacaoRequest):
    try:
        df_novos_dados = pd.DataFrame([extrair_dicionario(item) for item in dados.historico])
        if len(df_novos_dados) < 5:
            raise HTTPException(status_code=400, detail="Envie pelo menos 5 registros.")

        novo_modelo, r2, rmse = treinar_modelo_racao(df_novos_dados)
        salvar_modelo(novo_modelo, caminho_modelo_racao)
        modelos['racao'] = novo_modelo
        
        return {"mensagem": "Modelo de ração atualizado!", "r2": round(r2, 3), "rmse": round(rmse, 3)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao retreinar: {str(e)}")