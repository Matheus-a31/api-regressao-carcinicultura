from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import uuid
from schemas import BiomassaRequest, FCARequest 
from database import get_db, PrevisaoDB

router = APIRouter(tags=["Cálculos para gramatura e FCA"])


@router.get("/calcular/biomassa", summary="Listar todos os cálculos de biomassa salvos")
def listar_todos_calculos_biomassa(db: Session = Depends(get_db)):
    registros = db.query(PrevisaoDB).filter(PrevisaoDB.tipo == "calculo_biomassa").all()
    
    return [
        {
            "id": registro.id, 
            "parametros": registro.parametros_entrada, 
            "resultado_biomassa_kg": registro.resultado_estimado
        }
        for registro in registros
    ]

@router.get("/calcular/fca", summary="Listar todos os cálculos de FCA salvos")
def listar_todos_calculos_fca(db: Session = Depends(get_db)):
    registros = db.query(PrevisaoDB).filter(PrevisaoDB.tipo == "calculo_fca").all()
    
    return [
        {
            "id": registro.id, 
            "parametros": registro.parametros_entrada, 
            "resultado_fca": registro.resultado_estimado
        }
        for registro in registros
    ]


@router.post("/calcular/biomassa", summary="Calcular apenas a Biomassa")
def calcular_biomassa_endpoint(dados: BiomassaRequest, db: Session = Depends(get_db)):
    
    biomassa_estimada_kg = (dados.peso_atual_g * dados.densidade * dados.area_viveiro) * dados.sobrevivencia_est / 1000
    
    resultado_final = {
        "peso_informado_g": dados.peso_atual_g,
        "biomassa_total_estimada_kg": round(biomassa_estimada_kg, 2)
    }

    id_calculo = str(uuid.uuid4())
    novo_registro = PrevisaoDB(
        id=id_calculo, 
        tipo="calculo_biomassa", 
        parametros_entrada=dados.model_dump(), 
        resultado_estimado=resultado_final["biomassa_total_estimada_kg"] 
    )
    db.add(novo_registro)
    db.commit()

    return {
        "mensagem": "Cálculo de biomassa realizado com sucesso!",
        "id_banco": id_calculo,
        "indicadores_zootecnicos": resultado_final
    }

@router.get("/calcular/biomassa/{id_calculo}", summary="Buscar cálculo de biomassa salvo")
def buscar_calculo_biomassa(id_calculo: str, db: Session = Depends(get_db)):
    registro = db.query(PrevisaoDB).filter(PrevisaoDB.id == id_calculo, PrevisaoDB.tipo == "calculo_biomassa").first()
    if not registro:
        raise HTTPException(status_code=404, detail="Cálculo de biomassa não encontrado.")
    
    return {
        "id": registro.id, 
        "parametros": registro.parametros_entrada, 
        "resultado_biomassa_kg": registro.resultado_estimado
    }


@router.post("/calcular/fca", summary="Calcular apenas o FCA")
def calcular_fca_endpoint(dados: FCARequest, db: Session = Depends(get_db)):
    
    biomassa_estimada_kg = (dados.peso_atual_g * dados.densidade * dados.area_viveiro) * dados.sobrevivencia_est / 1000
    ganho_biomassa = biomassa_estimada_kg - dados.biomassa_inicial
    
    fca_estimado = (dados.racao_acumulada / ganho_biomassa) if ganho_biomassa > 0 else 0.0

    status_fca = "Excelente" if fca_estimado <= 1.5 else "Atenção" if fca_estimado <= 1.8 else "Prejuízo"

    resultado_final = {
        "ganho_biomassa_kg": round(ganho_biomassa, 2),
        "fca_estimado": round(fca_estimado, 2),
        "status_conversao": status_fca
    }

    id_calculo = str(uuid.uuid4())
    novo_registro = PrevisaoDB(
        id=id_calculo, 
        tipo="calculo_fca", 
        parametros_entrada=dados.model_dump(), 
        resultado_estimado=resultado_final["fca_estimado"] 
    )
    db.add(novo_registro)
    db.commit()

    return {
        "mensagem": "Cálculo de FCA realizado com sucesso!",
        "id_banco": id_calculo,
        "indicadores_zootecnicos": resultado_final
    }

@router.get("/calcular/fca/{id_calculo}", summary="Buscar cálculo de FCA salvo")
def buscar_calculo_fca(id_calculo: str, db: Session = Depends(get_db)):
    registro = db.query(PrevisaoDB).filter(PrevisaoDB.id == id_calculo, PrevisaoDB.tipo == "calculo_fca").first()
    if not registro:
        raise HTTPException(status_code=404, detail="Cálculo de FCA não encontrado.")
    
    return {
        "id": registro.id, 
        "parametros": registro.parametros_entrada, 
        "resultado_fca": registro.resultado_estimado
    }
    
