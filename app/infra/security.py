from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from app.infra.config import Settings

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login-form")