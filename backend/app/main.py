from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import accounts, categories, transactions, people, reports

# Create FastAPI app
app = FastAPI(
    title="Finance Tracker API",
    description="API for managing finance data"
)

# Configure CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
app.include_router(people.router, prefix="/people", tags=["people"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Finance Tracker API"}