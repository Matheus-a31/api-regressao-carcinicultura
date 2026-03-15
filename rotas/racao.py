from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
import pandas as pd
import uuid
import os
import math
from schemas import RacaoRequest, RetreinarRacaoRequest
from database import get_db, PrevisaoDB
from modelos.racao import prever_dias_restantes_racao, treinar_modelo_racao
from utils.persistencia import salvar_modelo
from config import CAMINHO_MODELOS

router = APIRouter(tags=["Consumo de Ração e Estoque"])
caminho_modelo_racao = os.path.join(CAMINHO_MODELOS, "modelo_racao.pkl")


@router.post("/prever/racao", summary="Prever consumo e dias de estoque")
def prever_consumo_racao(dados: RacaoRequest, request: Request, db: Session = Depends(get_db)):
    modelos = request.app.state.modelos
    if 'racao' not in modelos:
        raise HTTPException(status_code=503, detail="Modelo indisponível.")
    
    df_futuro = pd.DataFrame([item.model_dump() for item in dados.dados_futuros])
    
    try:
        dias_restantes = prever_dias_restantes_racao(modelos['racao'], dados.estoque_atual, df_futuro)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no modelo de previsão: {str(e)}")
    
    if math.isnan(dias_restantes) or math.isinf(dias_restantes):
        dias_restantes = 0.0 

    consumo_medio_diario = dados.estoque_atual / dias_restantes if dias_restantes > 0 else 0.0

    if math.isnan(consumo_medio_diario) or math.isinf(consumo_medio_diario):
        consumo_medio_diario = 0.0

    id_previsao = str(uuid.uuid4())
    
    try:
        novo_registro = PrevisaoDB(
            id=id_previsao, 
            tipo="racao", 
            parametros_entrada=dados.model_dump(), 
            resultado_estimado=round(dias_restantes, 1)
        )
        db.add(novo_registro)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar no banco de dados: {str(e)}")
    
    return {
        "mensagem": "Previsão de estoque calculada!",
        "id_banco": id_previsao,
        "consumo_medio_diario_kg": round(consumo_medio_diario, 2),
        "dias_restantes_estimados": round(dias_restantes, 1)
    }

@router.get("/prever/racao", summary="Listar todas as previsões de ração salvas")
def listar_todas_previsoes_racao(db: Session = Depends(get_db)):
    registros = db.query(PrevisaoDB).filter(PrevisaoDB.tipo == "racao").all()
    
    return [
        {
            "id": registro.id,
            "parametros": registro.parametros_entrada,
            "dias_restantes_estimados": registro.resultado_estimado
        }
        for registro in registros
    ]

@router.get("/prever/racao/{id_previsao}", summary="Buscar previsão de ração por ID")
def buscar_previsao_racao(id_previsao: str, db: Session = Depends(get_db)):
    registro = db.query(PrevisaoDB).filter(PrevisaoDB.id == id_previsao, PrevisaoDB.tipo == "racao").first()
    if not registro:
        raise HTTPException(status_code=404, detail="Previsão de ração não encontrada.")
    
    return {
        "id": registro.id,
        "parametros": registro.parametros_entrada,
        "dias_restantes_estimados": registro.resultado_estimado
    }

@router.post("/retreinar/racao", summary="Retreinar modelo de ração")
def retreinar_racao(dados: RetreinarRacaoRequest, request: Request):
    df_novos_dados = pd.DataFrame([item.model_dump() for item in dados.historico])
    if len(df_novos_dados) < 5:
        raise HTTPException(status_code=400, detail="Envie pelo menos 5 registros.")

    try:
        novo_modelo, r2, rmse = treinar_modelo_racao(df_novos_dados)
        salvar_modelo(novo_modelo, caminho_modelo_racao)
        request.app.state.modelos['racao'] = novo_modelo
        
        r2_seguro = 0.0 if math.isnan(r2) else round(r2, 3)
        rmse_seguro = 0.0 if math.isnan(rmse) else round(rmse, 3)

        return {
            "mensagem": "Modelo atualizado!", 
            "r2": r2_seguro, 
            "rmse": rmse_seguro
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao retreinar: {str(e)}")