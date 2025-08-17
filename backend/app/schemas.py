from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List  
import datetime as dt
from .models import TransactionType, ShareSource

# Account Schemas
class AccountBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    currency: str = Field(min_length=3, max_length=3)
    opening_balance: float = Field(ge=0)

class AccountCreate(AccountBase):
    pass

class AccountUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    opening_balance: Optional[float] = Field(default=None, ge=0)

class AccountOut(AccountBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: TransactionType

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    type: Optional[TransactionType] = None

class CategoryOut(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Person Schemas
class PersonBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    is_me: bool = Field(default=False)

class PersonCreate(PersonBase):
    pass

class PersonUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    is_me: Optional[bool] = None

class PersonOut(PersonBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Transaction Share Schemas
class TransactionShareBase(BaseModel):
    person_id: int
    amount_share: float = Field(ge=0.0, description="Must be greater than 0")
    source: ShareSource = Field(default=ShareSource.auto_default)

class TransactionShareCreate(TransactionShareBase):
    pass

class TransactionShareUpdate(BaseModel):
    person_id: Optional[int] = None
    amount_share: Optional[float] = None
    source: Optional[ShareSource] = None

class TransactionShareOut(TransactionShareBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Transaction Schemas
class TransactionBase(BaseModel):
    date: dt.date
    amount_total: float = Field(gt=0.0, description="Must be greater than 0")
    currency: str
    type: TransactionType
    description: Optional[str] = None
    account_id: int
    category_id: int
    payer_person_id: Optional[int] = None

class TransactionCreate(TransactionBase):
    shares: Optional[List[TransactionShareCreate]] = None

class TransactionUpdate(BaseModel):
    date: Optional[dt.date] = None
    amount_total: Optional[float] = None
    currency: Optional[str] = None
    type: Optional[TransactionType] = None
    description: Optional[str] = None
    account_id: Optional[int] = None
    category_id: Optional[int] = None
    payer_person_id: Optional[int] = None

class TransactionOut(TransactionBase):
    id: int
    shares: List[TransactionShareOut] = []
    model_config = ConfigDict(from_attributes=True)

# Report Schemas
class ReportBalance(BaseModel):
    account_id: int
    account_name: str
    balance: float

class ReportDebt(BaseModel):
    person_id: int
    person_name: str
    debt: float
    # If debt is 0, the person is not active
    is_active: bool

# Budget Schemas
class BudgetBase(BaseModel):
    name: str
    year: int
    month: int
    category_id: int
    amount: float

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    year: Optional[int] = None
    month: Optional[int] = None
    category_id: Optional[int] = None
    amount: Optional[float] = None

class BudgetOut(BudgetBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

