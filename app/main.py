# Comando de execução
# uvicorn main:app --reload

from fastapi import FastAPI
from app.api import api
from app.infra.database import Base, engine

app = FastAPI() 

app.include_router(api.api_router)

Base.metadata.create_all(engine)