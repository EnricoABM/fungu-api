from app.infra.database import engine
from sqlalchemy.orm import sessionmaker

def get_session():
    """Cria a sessão de banco de dados para serem usadas como dependencias"""
    try: 
        _Session = sessionmaker(bind=engine)
        session = _Session()
        yield session
    finally:
        session.close() 