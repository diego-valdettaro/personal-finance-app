from sqlalchemy import Integer, String, Boolean, Enum, Date, Float, ForeignKey, Text, UniqueConstraint, Index, CheckConstraint, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .database import Base
from typing import List, Optional
from datetime import datetime

#--------------------------------
# Enums
#--------------------------------
class AccountType(Enum):
    asset = "asset"
    liability = "liability"
    equity = "equity"
    income = "income"
    expense = "expense"

class TxSource(Enum):
    manual = "manual"
    batch_import = "batch_import"
    rule_based = "rule_based"

class TxType(Enum):
    income = "income"
    expense = "expense"
    transfer = "transfer"
    credit_card_payment = "credit_card_payment"
    forex = "forex"

class softDelete:
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

#--------------------------------
# Users
#--------------------------------
class User(Base, softDelete):
    __tablename__ = "users"

    # Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)
    home_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())

    # Relationships
    people: Mapped[List["Person"]] = relationship(back_populates="user")
    accounts: Mapped[List["Account"]] = relationship(back_populates="user")
    txs: Mapped[List["Transaction"]] = relationship(back_populates="user")
    budgets: Mapped[List["Budget"]] = relationship(back_populates="user")

#--------------------------------
# People
#--------------------------------
class Person(Base, softDelete):
    __tablename__ = "people"

    # Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_me: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # Foreign keys
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="people")
    splits: Mapped[List["TxSplit"]] = relationship(back_populates="person")

    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_person_user_name"),
        Index("uq_one_me_per_user", "user_id", unique=True, sqlite_where=Text("is_me = 1")),
    )

#--------------------------------
# Accounts
#--------------------------------
class Account(Base, softDelete):
    __tablename__ = "accounts"

    # Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[AccountType] = mapped_column(Enum(AccountType), nullable=False)
    currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    opening_balance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Foreign keys
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="accounts")
    postings: Mapped[List["TxPosting"]] = relationship(back_populates="account")
    budgets: Mapped[List["Budget"]] = relationship(back_populates="account")

    # Fields for credit cards
    billing_day: Mapped[int] = mapped_column(Integer, nullable=True)
    due_day: Mapped[int] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_account_user_name"),
        CheckConstraint(
            "(type IN ('asset', 'liability') AND currency IS NOT NULL) OR (type IN ('income', 'expense', 'equity') AND currency IS NULL)",
            name="ck_account_currency_required"
        ),
    )

#--------------------------------
# Transactions
#--------------------------------
class Transaction(Base, softDelete):
    __tablename__ = "transactions"

    # Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[datetime] = mapped_column(Date, nullable=False, default=func.now())
    type: Mapped[TxType] = mapped_column(Enum(TxType), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    amount_hc: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[TxSource] = mapped_column(Enum(TxSource), nullable=False, default=TxSource.manual)

    # Foreign keys
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="txs")
    postings: Mapped[List["TxPosting"]] = relationship(back_populates="tx")
    splits: Mapped[List["TxSplit"]] = relationship(back_populates="tx")

    # Constraints
    __table_args__ = (
        Index("idx_tx_user_id", "user_id"),
        CheckConstraint("amount_hc > 0", name="ck_tx_amount_positive"),
    )

#--------------------------------
# Postings
#--------------------------------
class TxPosting(Base):
    __tablename__ = "tx_postings"

    # Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    amount_oc: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    fx_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    amount_hc: Mapped[float] = mapped_column(Float, nullable=False)

    # Foreign keys
    tx_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"), nullable=False) 
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)

    # Relationships
    tx: Mapped["Transaction"] = relationship(back_populates="postings")
    account: Mapped["Account"] = relationship(back_populates="postings")

#--------------------------------
# TransactionSplit
#--------------------------------
class TxSplit(Base):
    __tablename__ = "tx_splits"

    # Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    share_amount: Mapped[float] = mapped_column(Float, nullable=False)

    # Foreign keys
    tx_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"), nullable=False)
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id"), nullable=False)

    # Relationships
    tx: Mapped["Transaction"] = relationship(back_populates="splits")
    person: Mapped["Person"] = relationship(back_populates="splits")

    # Constraints
    __table_args__ = (
        Index("idx_tx_split_person", "person_id"),
        CheckConstraint("share_amount > 0", name="ck_tx_split_amount_positive"),
    )

#--------------------------------
# Budgets
#--------------------------------
class Budget(Base):
    __tablename__ = "budgets"

    # Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    amount_oc: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    amount_hc: Mapped[float] = mapped_column(Float, nullable=False)	
    fx_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Foreign keys
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="budgets")
    account: Mapped["Account"] = relationship(back_populates="budgets")

    # Constraints
    __table_args__ = (
        Index("idx_budget_user_id", "user_id"),
        CheckConstraint("amount > 0", name="ck_budget_amount_positive"),
        UniqueConstraint("user_id", "account_id", "year", "month", name="uq_budget_user_account_year_month"),
    )