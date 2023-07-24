from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from src.db_internal import get_session
from src.models import DisplayColumn, SupportedDataTypes, DataDisplayType, CropType
from pydantic import BaseModel, ValidationError
from typing import Optional, List


router = APIRouter(prefix="/display-column", tags=["Display Column"])


'''
    Request Object - Create
        Display Column create request object
            - To be used in Post api to create a customer display column
            - Contains the required fields from the DisplayColumn model
            - Example:
                {
                    "customer_display_configuration_id": 1,
                    "column_label": "Tillage Depth",
                    "column_order": 1,
                    "is_active": true,
                    "data_type": "tillage_depth",
                    "data_display_type": "slider",
                    "data_options": ["0", "10", "1"]
                }
                For slider, data_options should be a list of 3 elements: [min, max, step]
'''
class CreateDisplayColumnRequest(BaseModel):
    customer_display_configuration_id: int
    column_label: str
    column_order: int
    is_active: bool
    data_type: SupportedDataTypes
    data_display_type: DataDisplayType
    data_options: List[str]


'''
    Create a customer display column with the above request object.
'''
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=DisplayColumn)
async def create_display_column(display_column: CreateDisplayColumnRequest, db: Session = Depends(get_session)):
    try:
        display_column = DisplayColumn.from_orm(display_column)
        db.add(display_column)
        db.commit()
        db.refresh(display_column)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=e.args[0])
    return display_column


'''
    Get all display columns for a customer display configuration.
'''
@router.get("/customer-config/{customer_display_config_id}", response_model=list[DisplayColumn])
async def get_display_columns_for_customer_display_config(customer_display_config_id: int, db: Session = Depends(get_session)):
    statement = select(DisplayColumn).where(DisplayColumn.customer_display_configuration_id == customer_display_config_id)
    results = db.execute(statement)
    results = list(i[0] for i in results.all())

    if len(results) == 0:
        return []
    return results


'''
    Request Object - Update
        Display Column update request object
            - To be used in Put api to update a customer display column
            - Keep the fields optional to allow partial updates
'''
class UpdateDisplayColumnRequest(BaseModel):
    customer_display_configuration_id: Optional[int]
    column_label: Optional[str]
    column_order: Optional[int]
    is_active: Optional[bool]
    data_type: Optional[SupportedDataTypes]
    data_display_type: Optional[DataDisplayType]
    data_options: Optional[List[str]]


'''
    Update a customer display column with the above request object.
    eg: To mark a column as inactive, send the following request:
        {
            "is_active": false
        }
'''
@router.put("/{display_column_id}", status_code=status.HTTP_200_OK, response_model=DisplayColumn)
async def update_display_column(display_column_id: int, update_col_data: UpdateDisplayColumnRequest, db: Session = Depends(get_session)):
    try:
        row = db.get(DisplayColumn, display_column_id)
        if not row:
            raise HTTPException(status_code=404, detail="display_column_id not found")

        for key, value in update_col_data:
            if value is not None:
                setattr(row, key, value)
        
        # Validate the rows with model validators
        DisplayColumn.validate(row)

        db.commit()
        db.refresh(row)
        return row
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=e.args[0])
    

'''
    Delete a customer display column.
'''
@router.delete("/{display_column_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_display_column(display_column_id: int, db: Session = Depends(get_session)):
    row = db.get(DisplayColumn, display_column_id)
    if not row:
        raise HTTPException(status_code=404, detail="display_column_id not found")
    db.delete(row)
    db.commit()
    return
