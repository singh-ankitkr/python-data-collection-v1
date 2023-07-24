from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel

from src.db_internal import get_session
from src.models import Customer


router = APIRouter(prefix="/customers", tags=["Customer"])


'''
      Customer Create Request
        - To be used in Post api to create a customer
        - Contains the required fields from the Customer model
        - Example:
            { 
                "name": "Customer Name",
                "is_active": true
            }
'''
class CustomerCreateRequest(BaseModel):
    name: str
    is_active: bool


@router.get("/", response_model=list[Customer])
async def get_customers(db: Session = Depends(get_session)):
    statement = select(Customer)
    results = db.execute(statement)
    results = list(i[0] for i in results.all())

    if len(results) == 0:
        return []
    return results


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Customer)
async def create_customer(customer_details: CustomerCreateRequest, db: Session = Depends(get_session)):
    try:
        customer = Customer.from_orm(customer_details)
        db.add(customer)
        db.commit()
        db.refresh(customer)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=e.args[0])
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(customer_id: int, db: Session = Depends(get_session)):
    row = db.get(Customer, customer_id)
    if not row:
        raise HTTPException(status_code=404, detail="customer_id not found")
    db.delete(row)
    db.commit()
    return