from typing import Annotated, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from sqlmodel import Session, select

from app.db import engine
from app.models import User


# Database session dependency
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

security = HTTPBasic()
# We use the CryptContext class to hash and verify passwords using the bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SessionDep = Annotated[Session, Depends(get_session)]

# Authentication dependency using HTTP Basic authentication
def get_current_user(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    session: SessionDep
):
    user = session.exec(select(User).where(User.username == credentials.username)).first()
    if not user or not pwd_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"}
        )
    return user