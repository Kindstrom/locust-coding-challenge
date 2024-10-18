import uuid
from typing import List

from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session, select

from app.models import CPUUsage, CPUUsageCreate, TestRun, User
from app.deps import SessionDep, pwd_context, get_current_user, get_session


router = APIRouter()


# Utility route to create new users easily
@router.post("/users/", response_model=User)
def create_user(user: User, session: SessionDep) -> User:
    user.hashed_password = pwd_context.hash(user.hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# Route that first logs in the user using the HTTP Basic authentication dependency, and then return its first and last name
@router.get("/login")
def login(user: User = Depends(get_current_user)):
    return {"first_name": user.first_name, "last_name": user.last_name}


# Route that fetches all cpu usage records for a given test run and user
@router.get("/test-run/{test_run_id}/cpu-usage", response_model=List[dict])
def get_cpu_usage(
    test_run_id: uuid.UUID,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    test_run = session.exec(
        select(TestRun).where(TestRun.id == test_run_id, TestRun.user_id == user.id)
    ).first()
    if not test_run:
        raise HTTPException(
            status_code=404, detail="Test run not found or does not belong to the user"
        )

    cpu_usages = session.exec(
        select(CPUUsage).where(CPUUsage.test_run_id == test_run_id)
    ).all()

    return [
        {"id": usage.id, "timestamp": usage.timestamp, "cpu_percent": usage.cpu_percent}
        for usage in cpu_usages
    ]


# Route to start a new test run
@router.post("/start-test-run")
def start_test_run(
    name: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    test_run = TestRun(name=name, user_id=user.id)
    session.add(test_run)
    session.commit()
    session.refresh(test_run)

    return {"message": "Test run started successfully", "test_run_id": test_run.id}


@router.post("/record-cpu-usage/{test_run_id}")
def record_cpu_usage(
    test_run_id: uuid.UUID,
    cpu_usage: CPUUsageCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # Check if the test run exists and belongs to the user
    test_run = session.exec(
        select(TestRun).where(TestRun.id == test_run_id, TestRun.user_id == user.id)
    ).first()
    if not test_run:
        raise HTTPException(
            status_code=404, detail="Test run not found or does not belong to the user"
        )

    # Create new record of CPU usage
    cpu_usage = CPUUsage(
        cpu_percent=cpu_usage.cpu_percent,
        test_run_id=test_run.id,
        timestamp=cpu_usage.timestamp,
    )
    session.add(cpu_usage)
    session.commit()

    return {
        "message": "CPU usage recorded successfully",
        "cpu_percent": cpu_usage.cpu_percent,
    }
