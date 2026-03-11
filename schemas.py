from pydantic import BaseModel, Field
from typing import List


class BiomassaRequest(BaseModel):
    peso_atual_g: float = Field(
        ..., 
        title="Peso Atual (g)",
        description="Peso médio atual do camarão aferido na biometria, em gramas.",
        gt=0,
        examples=[12.5]
    )
    densidade: float = Field(
        ...,
        title="Densidade de Povoamento",
        description="Quantidade de camarões estocados por metro quadrado (camarões/m²).",
        gt=0,
        examples=[80.0]
    )
    area_viveiro: float = Field(
        ...,
        title="Área do Viveiro (m²)",
        description="Área total do viveiro em metros quadrados.",
        gt=0,
        examples=[10000.0]
    )
    sobrevivencia_est: float = Field(
        ...,
        title="Sobrevivência Estimada (%)",
        description="Taxa de sobrevivência estimada do viveiro em porcentagem.",
        ge=0,
        le=100,
        examples=[85.0]
    )

# Schema exclusivo para o cálculo de FCA (Herda os campos de Biomassa)
class FCARequest(BiomassaRequest):
    biomassa_inicial: float = Field(
        ...,
        title="Biomassa Inicial (kg)",
        description="Biomassa total inicial no momento do povoamento, em quilogramas.",
        ge=0,
        examples=[50.0]
    )
    racao_acumulada: float = Field(
        ...,
        title="Ração Acumulada (kg)",
        description="Quantidade total de ração ofertada ao viveiro até o momento, em quilogramas.",
        ge=0,
        examples=[1500.0]
    )

class CondicaoFutura(BaseModel):
    dias_cultivo: int = Field(..., description="Dia futuro projetado", example=76)
    biomassa: float = Field(..., description="Biomassa total no tanque em kg", example=6375.0)
    temperatura: float = Field(..., description="Temperatura prevista em °C", example=30.5)
    taxa_arraçoamento: float = Field(..., description="Taxa de alimentação em decimal", example=0.03)

class RacaoRequest(BaseModel):
    estoque_atual: float = Field(..., description="Quantidade de ração disponível no estoque em kg", example=1500.0)
    dados_futuros: List[CondicaoFutura]

class DadosTreinamentoRacao(BaseModel):
    dias_cultivo: int = Field(..., example=60)
    biomassa: float = Field(..., example=240.0)
    temperatura: float = Field(..., example=31.0)
    taxa_arraçoamento: float = Field(..., example=0.08)
    consumo_diario: float = Field(..., description="VALOR REAL: Ração consumida no dia (kg)", example=11.5)

class RetreinarRacaoRequest(BaseModel):
    historico: List[DadosTreinamentoRacao]