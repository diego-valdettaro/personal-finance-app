from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .models import AccountType, TxSource, TxType

#--------------------------------
# User Schemas
#--------------------------------
class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: Optional[str] = None
    home_currency: str = Field(min_length=3, max_length=3)

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = Field(min_length=1, max_length=100)
    email: Optional[str] = None
    home_currency: Optional[str] = Field(min_length=3, max_length=3)

class UserOut(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

#--------------------------------
# Person Schemas
#--------------------------------

class PersonBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    is_me: bool = Field(default=False)

class PersonCreate(PersonBase):
    user_id: int

class PersonUpdate(BaseModel):
    name: Optional[str] = Field(min_length=1, max_length=100)
    is_me: Optional[bool] = Field(default=False)

class PersonOut(PersonBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

#--------------------------------
# Account Schemas
#--------------------------------
class AccountBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: AccountType
    currency: Optional[str] = Field(min_length=3, max_length=3)
    opening_balance: float = Field(ge=0.0)
    billing_day: Optional[int] = None
    due_day: Optional[int] = None

class AccountCreate(AccountBase):
    user_id: int

class AccountUpdate(BaseModel):
    name: Optional[str] = Field(min_length=1, max_length=100)
    type: Optional[AccountType] = None
    currency: Optional[str] = Field(min_length=3, max_length=3)
    opening_balance: Optional[float] = Field(ge=0.0)
    billing_day: Optional[int] = None
    due_day: Optional[int] = None

class AccountOut(AccountBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

#--------------------------------
# Posting Schemas
#--------------------------------
class TxPostingBase(BaseModel):
    amount_oc: float = Field()
    currency: str = Field(min_length=3, max_length=3)
    fx_rate: Optional[float] = None
    amount_hc: float = Field()

class TxPostingCreate(TxPostingBase):
    transaction_id: int
    account_id: int

class TxPostingCreateAutomatic(BaseModel):
    account_id: int
    amount_oc: Optional[float] = Field(default=None)
    currency: Optional[str] = Field(min_length=3, max_length=3, default=None)
    fx_rate: Optional[float] = None
    amount_hc: Optional[float] = Field(default=None)
    
class TxPostingUpdate(BaseModel):
    amount_oc: Optional[float] = Field(default=None)
    currency: Optional[str] = Field(min_length=3, max_length=3)
    fx_rate: Optional[float] = None
    amount_hc: Optional[float] = Field(default=None)

class TxPostingOut(TxPostingBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

#--------------------------------
# TxSplit Schemas
#--------------------------------
class TxSplitBase(BaseModel):
    share_amount: float = Field(ge=0.0)

class TxSplitCreate(TxSplitBase):
    transaction_id: int
    person_id: int

class TxSplitUpdate(BaseModel):
    share_amount: Optional[float] = Field(ge=0.0)

class TxSplitOut(TxSplitBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

#--------------------------------
# Tx Schemas
#--------------------------------
class TxBase(BaseModel):
    date: datetime
    type: TxType
    description: Optional[str] = None
    amount_hc: float = Field(gt=0.0)
    source: TxSource
    postings: list[TxPostingCreateAutomatic] = Field(default_factory=list)
    splits: list[TxSplitCreate] = Field(default_factory=list)

class TxCreate(TxBase):
    user_id: int

class TxUpdate(BaseModel):
    date: Optional[datetime] = None
    type: Optional[TxType] = None
    description: Optional[str] = None
    postings: Optional[list[TxPostingUpdate]] = None
    splits: Optional[list[TxSplitUpdate]] = None

class TxOut(TxBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

#--------------------------------
# Budget Schemas
#--------------------------------
class BudgetBase(BaseModel):
    name: str
    year: int

class BudgetLineCreate(BaseModel):
    month: int
    account_id: int
    amount_oc: float
    currency: str
    amount_hc: float
    fx_rate: Optional[float] = None
    description: Optional[str] = None

class BudgetCreate(BudgetBase):
    user_id: int
    lines: list[BudgetLineCreate]

class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    lines: Optional[list[BudgetLineCreate]] = None

class BudgetLineOut(BudgetLineCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class BudgetOut(BudgetBase):
    id: int
    lines: list[BudgetLineOut] = []
    model_config = ConfigDict(from_attributes=True)

#--------------------------------
# Report Schemas
#--------------------------------
class ReportBudgetProgress(BaseModel):
    account_id: int
    account_name: str
    budget_oc: float
    actual_oc: float
    progress: float

class ReportBalance(BaseModel):
    account_id: int
    account_name: str
    balance: float
    currency: str

class ReportDebt(BaseModel):
    person_id: int
    person_name: str
    debt: float
    # If debt is 0, the person is not active
    is_active: bool