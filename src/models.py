import re
from typing import Optional, List, Union
from datetime import datetime, date

from sqlmodel import Column, Field, SQLModel
from enum import Enum
from sqlmodel import SQLModel, Field
from sqlalchemy import JSON, Enum as SQLAlchemyEnum
from pydantic import validator



MIN_YEAR = 1980

'''
    DataDisplayType: How the data should be displayed on the UI.
'''
class DataDisplayType(str, Enum):
    slider = "slider"
    picklist = "picklist"
    text = "text"
    float = "float"
    boolean = "boolean"
    integer = "integer"


'''
    SupportedDataTypes: What does the data represent. Can be expanded by adding more relevant types.
'''
class SupportedDataTypes(str, Enum):
    tillage_depth = "tillage_depth"
    crop_type = "crop_type"
    comments = "comments"
    tilled = "tilled"
    external_account_id = "external_account_id"
    # Other data types which can be added in future.
    

'''
    CropType: Supported crop types. Can be expanded by adding more relevant types.
'''
class CropType(str, Enum):
    corn = "corn"
    soybean = "soybean"
    wheat = "wheat"
    hops = "hops"
    # Other crop types which can be added in future.


'''
    SupportedValueTypes: 
        - What is the actual type of the value.
        - Keeping this as we will store the value as string in the database.
'''
class SupportedValueTypes(str, Enum):
    int = "int"
    float = "float"
    str = "str"
    bool = "bool"
    date = "date"
    datetime = "datetime"


'''
    Customer: 
        - Customer of the application. 
        - A customer can have multiple users
'''
class Customer(SQLModel, table=True):
    __tablename__ = "customer"

    # Kept the id on Customer model (and others) as Optional and "default none" so that it can be absent on python object while creation
    # and Primary key so that it will be auto generated by the database
    # Standard practice with sqlmodel and fastapi.

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(description="Customer name")
    is_active: bool = Field(default=True, description="Is customer active")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    # Other customer fields...

    # Update the updated_at field on every update
    @classmethod
    def pre_save(cls, model: "Customer"):
        model.updated_at = datetime.now()
    
    @validator("name")
    def validate_name(cls, value):
        if len(value) == 0:
            raise Exception("Customer name should not be empty")
        return value


'''
     User: 
        - A customer can have multiple users
'''
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    customer_id: int = Field(foreign_key="customer.id")
    # Other user fields...

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Update the updated_at field on every update
    @classmethod
    def pre_save(cls, model: "User"):
        model.updated_at = datetime.now()
    
    @validator("name")
    def validate_name(cls, value):
        if len(value) == 0:
            raise Exception("User name should not be empty")
        return value
    
    @validator("email")
    def validate_email(cls, value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise Exception("Email must be valid.")
        return value


''' 
    Customer display configuration: 
        - A customer can have multiple display configurations
        - Each represents a particular view of the data
        - Users of a customer can select a display configuration to view.
'''
class CustomerDisplayConfiguration(SQLModel, table=True):
    __tablename__ = "customer_display_configuration"
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")
    display_name: str = Field(description="Display name of the configuration, like a heading of a presentation.")
    is_default: bool = Field(default=False, description="Is this the default configuration. May be used when a user logs in.")
    is_active: bool = Field(default=True, description="Is this configuration active")
    start_year: int = Field(description="Start year of the configuration")
    end_year: int = Field(description="End year of the configuration")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @classmethod
    def pre_save(cls, model: "Customer"):
        model.updated_at = datetime.now()

    @validator("display_name")
    def validate_display_name(cls, value):
        if len(value) == 0:
            raise Exception("Display name should not be empty")
        return value

    @validator("start_year")
    def validate_start_year(cls, value):
        if value < MIN_YEAR or value > date.today().year - 1:
            raise Exception(f"Start year should be between {MIN_YEAR} and previous year") 
        return value  

    @validator("end_year")
    def validate_end_year(cls, value, values):
        if value < values["start_year"]:
            raise Exception("End year should be greater than start year.") 
        
        if value < MIN_YEAR or value > date.today().year:
            raise Exception(f"End year should be between {MIN_YEAR} and current year inclusive.") 
        return value

'''
    DisplayColumn:
        - A display configuration can have multiple display columns
        - Each display_column represents the config of a particular column to be displayed
        - column_label:
            - Label of the column. Example: 'Tillage Depth', 'Crop Type', etc.
        - data_display_type:
            - slider: A slider to select a value
            - picklist: A picklist to select a value
            - text, float, boolean, integer: Fields to enter/display a value
        - data_type: 
            - What does this data represent. Example: tillage_depth, crop_type, etc.
            - Will also be used to map the data from the source_data table to the display column
        - data_options:
            - For slider: [min, max, step]
            - For picklist: [option1, option2, option3, ...]
            - For text, float, boolean, integer: Empty []
'''
class DisplayColumn(SQLModel, table=True):
    __tablename__ = "display_column"
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_display_configuration_id: int = Field( foreign_key= "customer_display_configuration.id", description="The display configuration this column belongs to")
    column_label: str = Field(description="Label of the column")
    column_order: int = Field(description="Order of the column in the display configuration")
    is_active: bool = Field(default=True, description="Is this column active")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    data_type: SupportedDataTypes = Field(description="What does this data represent. Example: tillage_depth, crop_type, etc.")

    data_display_type: DataDisplayType = Field(default=DataDisplayType.text, description="Type of the data to be displayed in the column")
    
    # Defining the db column as JSON as array is a valid json and sqlite doesn't support array type like postgres
    data_options: List[str] = Field(default=[], description="Options for the data display type", sa_column=Column(JSON))

    @classmethod
    def pre_save(cls, model: "DisplayColumn"):
        model.updated_at = datetime.now()
    
    @validator("data_options")
    def validate_data_options(cls, value, values):
        if values["data_display_type"] == DataDisplayType.slider:
            # Slider options should be [min, max, step] and should be string representation of float values
            if len(value) != 3:
                raise Exception("Slider options should be [min, max, step]")
            try:
                items = [float(item) for item in value]
            except:
                raise Exception("Slider options should be float values in string format")
            
            if values["data_type"] == SupportedDataTypes.tillage_depth:
                if items[0] < 0 or items[1] > 10 or items[2] <= 0:
                    raise Exception("Slider options for tillage depth should be [0, 10, step] where step > 0")
                
        if values["data_display_type"] == DataDisplayType.picklist:
            # Picklist options should be a non empty list of strings
            if len(value) == 0:
                raise Exception("Picklist options should not be empty")
            
            if values["data_type"] == SupportedDataTypes.crop_type:
                for val in value:
                    if val not in CropType.__members__:
                        raise Exception("Picklist options should be one of the crop types")
        return value
    
    @validator("column_order")
    def validate_column_order(cls, value):
        # Column order should be greater than 0
        if value < 0:
            raise Exception("Column order should be greater than 0")
        return value


'''
    SourceData:
        - Source table to contain the data which we need to be displayed/edited/filled by the user of a customer.
        - crop_cycle
            - Farms can have multiple crop cycles, like summer, spring, winter depending on the geography.
            - This field represents the crop cycle within a year, like 1, 2, 3, 4 for summer, spring, winter, fall.
        - Combination of year and crop_cycle can be used as a chronological order of the data.
'''
class SourceData(SQLModel, table=True):
    __tablename__ = "source_data"
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")

    year: int = Field(description="Year of the data")
    crop_cycle: int = Field(description="Crop cycle of the data")

    value_type: SupportedValueTypes = Field(default=SupportedValueTypes.str, description="Actual type of the value, like int, float, str, bool, date, datetime")
    value: str = Field(description="Data value in string representation")

    data_type: SupportedDataTypes = Field(description="What does this data represent. Example: tillage_depth, crop_type, etc.")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @classmethod
    def pre_save(cls, model: "SourceData"):
        model.updated_at = datetime.now()
    
    @validator("year")
    def validate_year(cls, value):
        if value < MIN_YEAR or value > date.today().year:
            raise Exception(f"Year should be between {MIN_YEAR} and current year inclusive.") 
        return value

    @validator("crop_cycle")
    def validate_crop_cycle(cls, value):
        if value < 1:
            raise Exception("Crop cycle should be greater that 0.") 
        return value
    
    @validator("value")
    def validate_value(cls, value, values):

        if values["data_type"] == SupportedDataTypes.tillage_depth:
            # Tillage depth should be between 0 and 10
            value = float(value)
            if value < 0 or value >= 10:
                raise Exception("Tillage depth should be between 0 (inclusive) and 10 ")
            
        elif values["data_type"] == SupportedDataTypes.crop_type:
            # Crop type should be one of the supported crop types
            if value not in CropType.__members__:
                raise Exception("Invalid crop type")
            
        elif values["data_type"] == SupportedDataTypes.tilled:
            # Tilled should be a boolean value. As we are storing it as string, we need to validate it for one of the true/false values.
            if value.lower() not in ["True", "False", "true", "false", "1", "0"]:
                raise Exception("Invalid value for tilled")
            
        elif values["data_type"] == SupportedDataTypes.external_account_id:
            # External account id should be alphanumeric
            if len(value) == 0:
                raise Exception("External account id should not be empty")
            if not re.match(r"^[a-zA-Z0-9_]*$", value):
                raise Exception("External account id must be alphanumeric.")

        else:
            return str(value)

        return str(value)

    
