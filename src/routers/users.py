from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from src.db_internal import get_session
from src.models import User
from pydantic import BaseModel


router = APIRouter(prefix="/users", tags=["User"])

class UserCreateRequest(BaseModel):
    name: str
    email: str
    customer_id: int


@router.get("/", response_model=list[User])
async def get_users(db: Session = Depends(get_session)):
    statement = select(User)
    results = db.execute(statement)
    results = list(i[0] for i in results.all())

    if len(results) == 0:
        return []
    return results


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Session = Depends(get_session)):
    row = db.get(User, user_id)
    if not row:
        raise HTTPException(status_code=404, detail="user_id not found")
    db.delete(row)
    db.commit()
    return


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=User)
async def create_user(user: UserCreateRequest, db: Session = Depends(get_session)):
    try:
        user = User.from_orm(user)
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=e.args[0])
    return user