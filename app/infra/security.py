from passlib.context import CryptContext
from app.infra.config import Settings

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
