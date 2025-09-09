from sqlalchemy import Integer, Numeric, String, Boolean, ForeignKey, text, UniqueConstraint, Index, CheckConstraint, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from enum import Enum as PyEnum
from sqlalchemy.types import Enum as SAEnum
from .database import Base
from typing import List, Optional
from datetime import datetime

#--------------------------------
# Enums
#--------------------------------
class AccountType(str, PyEnum):
    asset = "asset"
    liability = "liability"
    equity = "equity"
    income = "income"
    expense = "expense"

class TxSource(str, PyEnum):
    manual = "manual"
    batch_import = "batch_import"
    rule_based = "rule_based"

class TxType(str, PyEnum):
    income = "income"
    expense = "expense"
    transfer = "transfer"
    credit_card_payment = "credit_card_payment"
    forex = "forex"

class SoftDeleteMixin:
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

#--------------------------------
# User
#--------------------------------
class User(Base, SoftDeleteMixin):
    __tablename__ = "users"

    # Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    home_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())

    # Relationships
    people: Mapped[List["Person"]] = relationship(back_populates="user")
    accounts: Mapped[List["Account"]] = relationship(back_populates="user")
    txs: Mapped[List["Transaction"]] = relationship(back_populates="user")
    budgets: Mapped[List["BudgetHeader"]] = relationship(back_populates="user")

    # Constraints
    __table_args__ = (
        Index("uq_active_user_email", "email", unique=True, sqlite_where=text("active = 1")),
        CheckConstraint("char_length(home_currency) = 3", name="ck_user_home_currency_length"),
        CheckConstraint("(active = 0 AND deleted_at IS NOT NULL) OR (active = 1 AND deleted_at IS NULL)", name="ck_user_soft_delete_consistency"),
        Index("idx_user_active", "active"),
    )

#--------------------------------
# Person
#--------------------------------
class Person(Base, SoftDeleteMixin):
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
        CheckConstraint("(active = 0 AND deleted_at IS NOT NULL) OR (active = 1 AND deleted_at IS NULL)", name="ck_person_soft_delete_consistency"),
        Index("idx_person_active", "active"),
        Index("uq_one_me_per_user", "user_id", unique=True, sqlite_where=text("is_me = 1")),
        Index("uq_person_user_name_active", "user_id", "name", unique=True, sqlite_where=text("active = 1")),
    )

#--------------------------------
# Account
#--------------------------------
class Account(Base, SoftDeleteMixin):
    __tablename__ = "accounts"

    # Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[AccountType] = mapped_column(SAEnum(AccountType, name="account_type", native_enum=False), nullable=False)

    # For asset and liability accounts
    currency: Mapped[Optional[str]] = mapped_column(String(3))
    opening_balance: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    current_balance: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    bank_name: Mapped[Optional[str]] = mapped_column(String(100))
    billing_day: Mapped[Optional[int]] = mapped_column(Integer)
    due_day: Mapped[Optional[int]] = mapped_column(Integer)

    # Foreign keys
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="accounts")
    postings: Mapped[List["TxPosting"]] = relationship(back_populates="account")
    budget_lines: Mapped[List["BudgetLine"]] = relationship(back_populates="account", passive_deletes=True)

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_account_user_name"),
        CheckConstraint(
            "(type IN ('asset', 'liability') AND currency IS NOT NULL) OR (type IN ('income', 'expense', 'equity') AND currency IS NULL)",
            name="ck_account_currency_required"
        ),
    )

#--------------------------------
# FX rate
#--------------------------------
class FxRate(Base):
    __tablename__ = "fx_rates"

    # Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    from_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    to_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    rate: Mapped[float] = mapped_column(Numeric(18, 6), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)

    # Constraints
    __table_args__ = (
        UniqueConstraint("from_currency", "to_currency", "year", "month", name="uq_fx_rates_from_currency_to_currency_year_month"),
        Index("idx_fx_rates_from_currency_to_currency_year_month", "from_currency", "to_currency", "year", "month"),
        CheckConstraint("rate > 0", name="ck_fx_rate_positive"),
        CheckConstraint("month BETWEEN 1 AND 12", name="ck_fx_rate_month_range"),
    )

#--------------------------------
# Transaction
#--------------------------------

# Transaction Header
class Transaction(Base, SoftDeleteMixin):
    __tablename__ = "transactions"

    # Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())
    type: Mapped[TxType] = mapped_column(SAEnum(TxType, name="tx_type", native_enum=False), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    source: Mapped[TxSource] = mapped_column(SAEnum(TxSource, name="tx_source", native_enum=False), nullable=False, default=TxSource.manual)
    
    account_id_primary: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    amount_oc_primary: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    currency_primary: Mapped[str] = mapped_column(String(3), nullable=False)
    
    account_id_secondary: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    amount_oc_secondary: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    currency_secondary: Mapped[Optional[str]] = mapped_column(String(3))

    # absolute value of the first posting amount in the home currency of the user
    tx_amount_hc: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))

    # Foreign keys
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="txs")
    postings: Mapped[List["TxPosting"]] = relationship(back_populates="tx")
    splits: Mapped[List["TxSplit"]] = relationship(back_populates="tx")

    # Constraints
    __table_args__ = (
        Index("idx_tx_user_id", "user_id"),
        CheckConstraint("tx_amount_hc > 0", name="ck_tx_amount_positive"),
        CheckConstraint("amount_oc_primary > 0", name="ck_tx_amount_oc_primary_positive"),
        CheckConstraint("amount_oc_secondary IS NULL OR amount_oc_secondary > 0", name="ck_tx_amount_oc_secondary_positive"),
    )

# Transaction Posting
class TxPosting(Base, SoftDeleteMixin):
    __tablename__ = "tx_postings"

    # Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # absolute value of first posting amount in the home currency of the user
    amount_oc: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    fx_rate: Mapped[Optional[float]] = mapped_column(Numeric(18, 6))
    amount_hc: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)

    # Foreign keys
    tx_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"), nullable=False) 
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)

    # Relationships
    tx: Mapped["Transaction"] = relationship(back_populates="postings")
    account: Mapped["Account"] = relationship(back_populates="postings")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("amount_oc <> 0", name="ck_tx_posting_amount_oc_not_zero"),
        CheckConstraint("amount_hc <> 0", name="ck_tx_posting_amount_hc_not_zero"),
        CheckConstraint("(amount_oc > 0 AND amount_hc > 0) OR (amount_oc < 0 AND amount_hc < 0)", name="ck_tx_posting_sign_consistent"),
        CheckConstraint("char_length(currency) <= 3", name="ck_tx_posting_currency_length"),
        CheckConstraint("fx_rate IS NULL OR fx_rate > 0", name="ck_tx_posting_fx_rate_positive"),
    )

# Transaction Split
class TxSplit(Base, SoftDeleteMixin):
    __tablename__ = "tx_splits"

    # Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    share_amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)

    # Foreign keys
    tx_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"), nullable=False)
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id"), nullable=False)

    # Relationships
    tx: Mapped["Transaction"] = relationship(back_populates="splits")
    person: Mapped["Person"] = relationship(back_populates="splits")

    # Constraints
    __table_args__ = (
        Index("idx_tx_split_person", "person_id"),
        UniqueConstraint("tx_id", "person_id", name="uq_tx_split_tx_person"),
        CheckConstraint("share_amount > 0", name="ck_tx_split_amount_positive"),
    )

#--------------------------------
# Budget
#--------------------------------

# Budget Header
class BudgetHeader(Base):
    __tablename__ = "budget_headers"

    # Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Foreign keys
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)    

    # Relationships
    user: Mapped["User"] = relationship(back_populates="budgets")
    budget_lines: Mapped[List["BudgetLine"]] = relationship(
        back_populates="header",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Constraints
    __table_args__ = (
        Index("idx_budget_header_user_id", "user_id"),
        UniqueConstraint("user_id", "name", "year", name="uq_budget_header_user_name_year"),
    )

# Budget Line
class BudgetLine(Base):
    __tablename__ = "budget_lines"
    
    # Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    amount_oc: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    amount_hc: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)	
    fx_rate: Mapped[Optional[float]] = mapped_column(Numeric(18, 6))
    description: Mapped[Optional[str]] = mapped_column(String(100))

    # Foreign keys
    header_id: Mapped[int] = mapped_column(ForeignKey("budget_headers.id", ondelete="CASCADE"), nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    header: Mapped["BudgetHeader"] = relationship(back_populates="budget_lines", passive_deletes=True)
    account: Mapped["Account"] = relationship(back_populates="budget_lines")
    
    # Constraints
    __table_args__ = (
        Index("idx_budget_line_header_id", "header_id"),
        Index("idx_budget_line_account_id", "account_id"),
        CheckConstraint("month BETWEEN 1 AND 12", name="ck_budget_line_month_range"),
        CheckConstraint("amount_oc >= 0", name="ck_budget_line_amount_oc_non_negative"),
        CheckConstraint("amount_hc >= 0", name="ck_budget_line_amount_hc_non_negative"),
        CheckConstraint("fx_rate IS NULL OR fx_rate > 0", name="ck_budget_line_fx_rate_positive"),
        CheckConstraint("char_length(currency) <= 3", name="ck_budget_line_currency_length"),
        Index("uq_active_budget_line_header_account_month", "header_id", "account_id", "month", unique=True, sqlite_where=text("active = 1")),
    )