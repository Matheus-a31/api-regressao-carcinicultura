from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.dialects.postgresql import JSONB 
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# --- A MÁGICA ACONTECE AQUI ---
# pool_pre_ping=True: Testa a conexão antes de cada requisição. Se o Neon tiver fechado, ele reconecta.
# pool_recycle=300: Força a reciclagem da conexão a cada 5 minutos, evitando que ela fique velha.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PrevisaoDB(Base):
    __tablename__ = "previsoes"

    id = Column(String, primary_key=True, index=True)
    tipo = Column(String, index=True)
    
    parametros_entrada = Column(JSONB) 
    
    resultado_estimado = Column(Float)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()