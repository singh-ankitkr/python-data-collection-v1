from fastapi import FastAPI, HTTPException, status
from sqlmodel import select, Session
from sqlalchemy import event
from sqlalchemy.engine import Engine

from .db_internal import create_db
from .routers.users import router as users_router
from .routers.customers import router as customers_router
from .routers.customerDisplayConfigurations import router as customer_display_config_router
from .routers.displayColumns import router as display_columns_router


app = FastAPI()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@app.on_event("startup")
async def startup_event():
    create_db()


app.include_router(users_router)
app.include_router(customers_router)
app.include_router(customer_display_config_router)
app.include_router(display_columns_router)

