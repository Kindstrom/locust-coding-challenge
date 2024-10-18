from sqlmodel import SQLModel, create_engine
from app.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=True)


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db() -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel
    # This works because the models are already imported and registered from app.models
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    init_db()
