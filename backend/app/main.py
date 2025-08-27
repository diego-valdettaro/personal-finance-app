from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import accounts, transactions, people, reports, budgets, users
from .database import Base, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown (if needed)

# Create FastAPI app
app = FastAPI(
    title="Finance Tracker API",
    description="API for managing finance data",
    lifespan=lifespan
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
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(people.router)
app.include_router(reports.router)
app.include_router(budgets.router)
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Finance Tracker API"}