from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, EmailStr

from .models import AccountType, TxSource, TxType

#--------------------------------
# User Schemas
#--------------------------------
class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=255)
    home_currency: str = Field(min_length=3, max_length=3)

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = Field(None, max_length=255)
    home_currency: Optional[str] = Field(None, min_length=3, max_length=3)

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
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_me: Optional[bool] = None

class PersonOut(PersonBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

#--------------------------------
# Account Schemas
#--------------------------------
class AccountBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: AccountType

class AccountCreateIncomeExpense(AccountBase):
    user_id: int
    model_config = ConfigDict(extra="forbid")

class AccountCreateAsset(AccountBase):
    user_id: int
    currency: str = Field(min_length=3, max_length=3)
    bank_name: Optional[str] = None
    opening_balance: Optional[float] = Field(None, ge=0.0)

class AccountCreateLiability(AccountCreateAsset):
    billing_day: Optional[int] = Field(None, ge=1, le=31)
    due_day: Optional[int] = Field(None, ge=1, le=31)

class AccountUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[AccountType] = None
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    bank_name: Optional[str] = None
    opening_balance: Optional[float] = Field(None, ge=0.0)
    billing_day: Optional[int] = None
    due_day: Optional[int] = None

class AccountOut(AccountBase):
    id: int
    currency: Optional[str] = None
    bank_name: Optional[str] = None
    opening_balance: Optional[float] = None
    billing_day: Optional[int] = None
    due_day: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

#--------------------------------
# FX Rate Schemas
#--------------------------------
class FxRateBase(BaseModel):
    from_currency: str = Field(min_length=3, max_length=3)
    to_currency: str = Field(min_length=3, max_length=3)
    rate: float = Field(gt=0.0)
    year: int
    month: int

class FxRateCreate(FxRateBase):
    pass

class FxRateUpdate(BaseModel):
    rate: Optional[float] = Field(gt=0.0)

class FxRateOut(FxRateBase):
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

class TxPostingCreateAutomatic(BaseModel):
    account_id: int
    amount_oc: Optional[float] = None
    currency: Optional[str] = None
    fx_rate: Optional[float] = None
    amount_hc: Optional[float] = None

class TxPostingOut(TxPostingBase):
    id: int
    tx_id: int
    account_id: int
    model_config = ConfigDict(from_attributes=True)

#--------------------------------
# TxSplit Schemas
#--------------------------------
class TxSplitBase(BaseModel):
    share_amount: float = Field(gt=0.0)

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
    source: TxSource = TxSource.manual
    amount_oc_primary: float
    currency_primary: str = Field(min_length=3, max_length=3)

    # Account for the first posting - origin account
    account_id_primary: int
    # Account for the second posting - destination account
    account_id_secondary: int

class TxCreate(TxBase):
    user_id: int

class TxCreateForex(TxBase):
    user_id: int
    amount_oc_secondary: float
    currency_secondary: str = Field(min_length=3, max_length=3)

class TxUpdate(BaseModel):
    date: Optional[datetime] = None
    type: Optional[TxType] = None
    description: Optional[str] = None

    # Editable financial fields
    amount_oc_primary: Optional[float] = None
    currency_primary: Optional[str] = None
    account_id_primary: Optional[int] = None
    account_id_secondary: Optional[int] = None

    # Editable fx fields
    amount_oc_secondary: Optional[float] = None
    currency_secondary: Optional[str] = None

class TxOut(TxBase):
    id: int
    active: bool

    # Derived values from the first posting
    tx_amount_hc: float

    postings: list[TxPostingOut] = Field(default_factory=list)
    splits: list[TxSplitOut] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

#--------------------------------
# Budget Schemas
#--------------------------------
class BudgetBase(BaseModel):
    name: str = Field(min_length=1, max_length=20)
    year: int

class BudgetLineCreate(BaseModel):
    month: int = Field(ge=1, le=12)
    account_id: int
    amount_oc: float
    currency: str = Field(min_length=3, max_length=3)
    amount_hc: float
    fx_rate: Optional[float] = None
    description: Optional[str] = Field(default=None, max_length=100)

class BudgetCreate(BudgetBase):
    user_id: int
    lines: list[BudgetLineCreate]

class BudgetLineUpsert(BaseModel):
    id: Optional[int] = None
    month: int = Field(ge=1, le=12)
    account_id: int
    amount_oc: float
    currency: str = Field(min_length=3, max_length=3)
    amount_hc: float
    fx_rate: Optional[float] = None
    description: Optional[str] = Field(default=None, max_length=100)

class BudgetUpdate(BaseModel):
    name: Optional[str] = Field(min_length=1, max_length=20)
    year: Optional[int] = None
    lines: list[BudgetLineUpsert]

class BudgetLineOut(BudgetLineCreate):
    id: int
    header_id: int
    model_config = ConfigDict(from_attributes=True)

class BudgetOut(BudgetBase):
    id: int
    lines: list[BudgetLineOut] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

#--------------------------------
# Report Schemas
#--------------------------------
class ReportBudgetProgress(BaseModel):
    account_id: int
    account_name: str
    budget_hc: float
    actual_hc: float
    progress: float

class ReportBalance(BaseModel):
    account_id: int
    account_name: str
    balance: float
    currency: str = Field(min_length=3, max_length=3)

class ReportDebt(BaseModel):
    person_id: int
    person_name: str
    debt: float
    # If debt is 0, the person is not active
    is_active: bool