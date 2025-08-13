from pydantic import BaseModel, Field, ConfigDict, conlist
from typing import Optional, Literal, List
import datetime as dt

from sqlalchemy import Transaction

# Account Schemas
class AccountBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    currency: str = Field(min_length=3, max_length=3)

class AccountCreate(AccountBase):
    pass

class AccountUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)

class AccountOut(AccountBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: Literal["expense", "income"]

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    type: Optional[Literal["expense", "income"]] = None

class CategoryOut(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Transaction Schemas
class TransactionBase(BaseModel):
    date: dt.date
    amount: float = Field(gt=0, description="Must be greater than 0")
    currency: str
    type: Literal["expense", "income"]
    description: Optional[str] = None
    detail_json: Optional[str] = None
    account_id: int
    category_id: int

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    date: Optional[dt.date] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    type: Optional[Literal["expense", "income"]] = None
    description: Optional[str] = None
    detail_json: Optional[str] = None
    account_id: Optional[int] = None
    category_id: Optional[int] = None

class TransactionOut(TransactionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)