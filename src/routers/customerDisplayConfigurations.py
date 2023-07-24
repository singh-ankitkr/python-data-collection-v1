from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from src.db_internal import get_session
from src.models import CustomerDisplayConfiguration
from pydantic import BaseModel, ValidationError
from typing import Optional


router = APIRouter(prefix="/customer-display-config", tags=["Customer Display Configuration"])


'''
    Request Object - Create
        Customer Display Configuration create request object
            - To be used in Post api to create a customer display configuration
            - Contains the required fields from the CustomerDisplayConfiguration model
            - Example:
                {
                    
                    "customer_id": 1,
                    "display_name": "Customer Display Name 1",
                    "is_default": true,
                    "is_active": true,
                    "start_year": 2013,
                    "end_year": 2022
                }
'''
class CreateCustomerDisplayConfigurationRequest(BaseModel):
    customer_id: int
    display_name: str
    is_default: bool
    is_active: bool
    start_year: int
    end_year: int


'''
    Create a customer display configuration with the above request object.
'''
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CustomerDisplayConfiguration)
async def create_display_config(display_config: CreateCustomerDisplayConfigurationRequest, db: Session = Depends(get_session)):
    try:
        display_config = CustomerDisplayConfiguration.from_orm(display_config)
        db.add(display_config)
        db.commit()
        db.refresh(display_config)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=e.args[0])
    return display_config


'''
    Get all display configurations.
'''
@router.get("/", response_model=list[CustomerDisplayConfiguration])
async def get_all_display_configs(db: Session = Depends(get_session)):
    statement = select(CustomerDisplayConfiguration)
    results = db.execute(statement)
    results = list(i[0] for i in results.all())

    if len(results) == 0:
        return []
    return results


'''
    Get a display configuration by id.
'''
@router.get("/{display_config_id}", response_model=CustomerDisplayConfiguration)
async def get_display_config_by_id(display_config_id: int, db: Session = Depends(get_session)):
    display_cofig = db.get(CustomerDisplayConfiguration, display_config_id)
    if not display_cofig:
        raise HTTPException(status_code=404, detail="display_config_id not found")
    return display_cofig


'''
    Delete a display configuration by id.
'''
@router.delete("/{display_config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_display_config_by_id(display_config_id: int, db: Session = Depends(get_session)):
    display_cofig = db.get(CustomerDisplayConfiguration, display_config_id)
    if not display_cofig:
        raise HTTPException(status_code=404, detail="display_config_id not found")
    db.delete(display_cofig)
    db.commit()
    return


'''
    Request Object - Update
        Customer Display Configuration update request object
        Keeping the fields optional to allow partial updates
'''
class UpdateCustomerDisplayConfigurationRequest(BaseModel):
    customer_id: Optional[int] = None
    display_name: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None

    
'''
    Update a display configuration by id
'''
@router.put("/{display_config_id}", status_code=status.HTTP_200_OK, response_model=CustomerDisplayConfiguration)
async def update_display_config_by_id(display_config_id: int, update_config_data: UpdateCustomerDisplayConfigurationRequest, db: Session = Depends(get_session)):
    try:
        row = db.get(CustomerDisplayConfiguration, display_config_id)
        if not row:
            raise HTTPException(status_code=404, detail="display_config_id not found")
        
        # update the row with the request object values.
        for key, value in update_config_data:
            if value is not None:
                setattr(row, key, value)
        
        # validate the row with the updated values.
        CustomerDisplayConfiguration.validate(row.dict())

        db.commit()
        db.refresh(row)
        return row
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=e.args[0])

