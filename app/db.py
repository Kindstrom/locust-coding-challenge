from sqlmodel import SQLModel, Session, create_engine, select
from app.config import settings
from app.models import User

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=True)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)

    from app.deps import pwd_context

    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.username == settings.INITIAL_USER_USERNAME)
        ).first()
        if not user:
            user = User(
                first_name=settings.INITIAL_USER_FIRSTNAME,
                last_name=settings.INITIAL_USER_LASTNAME,
                username=settings.INITIAL_USER_USERNAME,
                hashed_password=pwd_context.hash(settings.INITIAL_USER_PASSWORD),
            )
            session.add(user)
            session.commit()
            session.refresh(user)


if __name__ == "__main__":
    init_db()
