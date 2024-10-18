from datetime import datetime
from typing import List
import uuid
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)
    username: str = Field(max_length=255)
    hashed_password: str
    test_runs: List["TestRun"] = Relationship(back_populates="user")


class TestRun(SQLModel, table=True):
    __tablename__: str = "test_run"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    start_time: datetime = Field(default_factory=datetime.now)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="test_runs")
    cpu_usages: List["CPUUsage"] = Relationship(back_populates="test_run")

class CPUUsage(SQLModel, table=True):
    __tablename__: str = "cpu_usage"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.now)
    cpu_percent: float
    test_run_id: uuid.UUID = Field(foreign_key="test_run.id")
    test_run: TestRun = Relationship(back_populates="cpu_usages")
