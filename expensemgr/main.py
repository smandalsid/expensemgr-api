from fastapi import FastAPI
from expensemgr.database.db import engine, Base

from expensemgr.routers import auth, users, expense, currency
from expensemgr.utils.logger import expense_mgr_logger

app = FastAPI(
    title = "API of Expense Manager Application",
    summary = "This API will give the complete functionality of an expense manager application with user management, admin functionality, creating currencies, adding. sharing and managing expenses",
    servers=[
        {"url": "http://127.0.0.1:8000", "description": "Local environment"},
    ]
)

Base.metadata.create_all(bind=engine)

@app.get("/health")
async def get_health_check():
    return {"Message": "Application looks healthy"}


# include all routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(expense.router)
app.include_router(currency.router)