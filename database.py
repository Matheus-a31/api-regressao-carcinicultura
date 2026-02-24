# database.py
from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.dialects.postgresql import JSONB # O Postgres tem um formato JSON super otimizado!
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

# Carrega a URL do seu PostgreSQL do arquivo .env
load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Cria a conexão com o banco
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- ESTRUTURA DA TABELA NO POSTGRES ---
class PrevisaoDB(Base):
    __tablename__ = "previsoes"

    id = Column(String, primary_key=True, index=True)
    tipo = Column(String, index=True) # Vai salvar se é "gramatura" ou "racao"
    
    # O JSONB é um superpoder do Postgres! Ele salva os parâmetros de forma estruturada.
    parametros_entrada = Column(JSONB) 
    
    resultado_estimado = Column(Float)

# Manda o Postgres criar a tabela "previsoes" se ela ainda não existir
Base.metadata.create_all(bind=engine)

# Função para abrir e fechar a conexão do banco a cada requisição da API
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()