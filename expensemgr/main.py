from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from expensemgr.database.db import Base, DB
from expensemgr.routers import auth, currency, expense, users, exchange_rate

app = FastAPI(
    title="API of Expense Manager Application",
    summary="This API will give the complete functionality of an expense manager application with user management, admin functionality, creating currencies, adding. sharing and managing expenses",
    servers=[
        {"url": "https://expensemgr-api.vercel.app", "description": "Prod Environment"},
        {"url": "https://expensemgr-api-git-development-catalystmandal-1458s-projects.vercel.app", "description": "Preview Environment"},
        {"url": "http://127.0.0.1:8000", "description": "Local environment"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://expensemgr-ui.vercel.app"],
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type", "x-vercel-protection-bypass"],
)

@app.get("/health")
async def get_health_check():
    return {"Message": "Application looks healthy"}

# include all routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(expense.router)
app.include_router(currency.router)
app.include_router(exchange_rate.router)

