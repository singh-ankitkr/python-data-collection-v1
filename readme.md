# Assumptions
### Crop Cycles
 - In a year a customer can have multiple crop cycles depending on the regions, weather conditions, etc.
    - I have created a field crop_cycle to store this information.
    - It is an integer with a value 1, 2, 3, 4 etc, which internally may mean different crop cycles of a year like summer, spring, winter, fall, etc.
    - A combination of year and crop_cycle uniquely determines the chronology of associated data

### Customer and Users
 - A customer can have multiple users.
    - There can be multiple users associated with a customer
    - They all can see all the different combination/view of the data.
    - Have created the display configurations associated with Customer rather than users.

### Minimum and Maximum year
- Assumed that the minimum year we wish to collect from is 1980. This is completely arbitrary and can be changed as per the context.
- Assumed that the maximum year we wish to collect is the current year. It causes a limitation that data can be filled for upcoming crop_cycles of the year.

### Supported Data Types 
- These are the different of data entities we want to collect from the customer.
- Currently only supporting these via an enum
    - tillage_depth (Depth of tillage)
    - crop_type
    - comments
    - tilled (A boolean)
    - external_account_id
- It is expandable by adding more data dimension to the enum and adding appropriate validations for them.

### Supported Display Types
- Assumed that the display types we are supporting are
    - slider
    - picklist
    - text
    - float, boolean and integer
- Based on this assumption written validation logic for these display types.
- In the future we may want to expand it to include some other display types. Its an enum and in a way extensible by adding more to it (along with writing the corresponding validations.)


### Supported Crop Types
- Its an enum with the crops
    - corn
    - soybean
    - wheat
    - hops
- Can be expanded by adding more crops to the enum.


# Deployment
### Running the server locally
- clone the repository
- From terminal
    - cd into the repository
    - pip install -r requirements
    - uvicorn src.main:app --reload --workers 1
- The api documentation (swagger) would be available on urls
    - `http://localhost:8000/docs` (For running and testing the apis.)
    - `http://localhost:8000/redoc` (For checking the request/response definition.)

### Running the tests
- From terminal (option 1)
    - `rm -f test.db`
    - `db_path="test.db" pytest -x -vv`
- From makefile (option 2)
    - Run the `test` section of the file `makefile`


# Implementation Logic
### CustomerDisplayConfiguration
    This represents a particular tabular view for a customer

### DisplayColumn
- This represents a particular column in a CustomerDisplayConfiguration (tabular view).

    - The combination of the fields `data_display_type` and `data_options` can be used to define how we want to display a field.
        - example 1: For `data_display_type` of `"picklist"` and `data_options` as `["wheat", "corn", "soybean", "hops"]` can be used to display a picklist with the array values `["wheat", "corn", "soybean", "hops"]` as picklist items to select from
        - example 2: `"slider"` (`data_display_type`) and `"[0, 10, 0.1]"` (`data_options`) denotes a slider on the frontend with the left value as 0, rightmost as 10 and a slide step of 0.1
        - As of now, for other types of `data_display_type` (text, boolean, float, integer), `data_options` has no meaning should be empty.

    - data_type represents the data dimension (`tillage_depth, crop_type, tilled, etc`) this column displays.
        - It is particularly important as it used to map the data from source table `SourceData`, to a particular row based on the chronology (`year` and `crop_cycle` combination)

### SourceData
- Assumption/Representation of how the `SourceData` table. 
    - Combination of `year` and `crop_cycle` tells us when this data is for.
    - `value` stores the value of the data entity as a string.
    - `data_type` (`tillage_depth, crop_type, tilled, etc`) tells what the value represents.
        - Logic for having `data_type` on both `SourceData` and `DisplayColumn`
            - To show the values for a particular `customer`, between a `start_year` and `end_year` (based on a `CustomerDisplayRepresentation`) I am thinking the following steps
                - step 1: Get all data points (all `SourceData`) where the `year` lies between start and end years.
                - step 2: Group the data by combination of `year` and `crop_cycle`. (lets call it a row)
                - step 3: Sort the rows in `descending` order based on combination of `year` and `crop_cycle`. (chronologically sorted rows in descending order)

                - step 5: Get all the `DisplayColumn`s for the particular `CustomerDisplayConfiguration` which are `is_active`
                - step 6: Map the data entities in the row (from step 3) with the `DisplayColumn` objects using matching `data_type` on both `SourceData` and `DisplayColumn`
                - step 7: Use `column_order` from corresponding `DisplayColumn` object to place data entity of row from `SourceData` to appropriate column.
        - Also, the year goes to the leftmost position.
            - All other entities are placed column wise in a row on the basis of ascending `column_order`
    - `value_type` - This is not being used currently, but it stores the type of the value (int, float, bool, etc) we are storing as string. Can later be useful.
    

# Validations
- The model validators are written in the models using the fastApi decorator @validator.

# Pros
- Expandable design and can be easily expanded to display other display_types and data entities
- View related configs are separate from data.
    - All view related configs are in CustomerDisplayConfiguration and DisplayColumn
    - SourceData only contains data and information related to data
    - This makes it possible to have data without duplicacy and easier maintainence of source of truth.

# Cons
- All data is stored as its string format, which makes queries which depend on arithmatic operations on those data difficult.
    - example - sql query to get all the years where tillage_depth was more that 6, would be more difficult
- All data entities are generalized and stored in the same format, making queries which depend of multiple data entities difficult.
    - example - sql query to get all years where the `crop_type` was `wheat` and the customer got his farmland `tilled`, (This would not be trivial)

# Alternate Solutions
- Store the data in a table with exhaustive columns
    - id | tillage_depth | tilled | crop_type | comments | external_account_id | ...other fields... | created_at | updated_at
    - For adding new field the table would need to be updated
- Store the display configurations as JSON either in postgres or in some document based data store.
    - id | customer_id | display_config | created_at | updated_at
    where display_config can be JSON
    `{columns: [{data_type: "tilled_depth", display_order: 1, display_type: "slider", display_options: [0, 10, 0.5]}, {data_type: "crop_type", display_order: 2, display_type: "picklist", display_options: ["wheat", "corn"]} , {"comments", display_order: 3, display_type: "text"}]}`


# API requests
- The api documentation (swagger) would be available on urls (Option 1)
    - `http://localhost:8000/docs` (For running and testing the apis.)
    - `http://localhost:8000/redoc` (For checking the request/response definition.)

- The file `request_doc.json` can be imported to `POSTMAN` rest api client. (Option 2)

- The test file `test_apis.py` also contains apis which are called with sample data.
