from sqlalchemy import Column, Integer, String, Boolean, Enum, Date, Float, ForeignKey, Text, UniqueConstraint, Index, CheckConstraint
from sqlalchemy.orm import relationship
from .database import Base
import enum

# Enums

class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"

class ShareSource(str, enum.Enum):
    # Expense attributable to me by default
    auto_default = "auto_default"
    # Expense attributed manually
    user_manual = "user_manual"
    # Expense attributable by debt income
    auto_debt_income = "auto_debt_income"

# Models

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    currency = Column(String(3), nullable=False, default="EUR")
    opening_balance = Column(Float, nullable=False, default=0.0)
    # If an account is deleted, all transactions associated with it are deleted
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    type = Column(Enum(TransactionType), nullable=False)
    # If a category is deleted, all transactions associated with it are deleted 
    transactions = relationship("Transaction", back_populates="category", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="category", cascade="all, delete-orphan")

class Person(Base):
    __tablename__ = "people"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    is_me = Column(Boolean, nullable=False, default=False)
    # If a person is deleted, all transactions associated with them are deleted
    transactions_paid = relationship("Transaction", back_populates="payer", foreign_keys="Transaction.payer_person_id", cascade="all, delete-orphan")
    # If a person is deleted, all shares associated with them are deleted
    shares = relationship("TransactionShare", back_populates="person", cascade="all, delete-orphan")
    # Ensure that there is exactly 1 "me"
    __table_args__ = (Index("uq_one_me", "is_me", unique=True, sqlite_where=Text("is_me = 1")),)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    amount_total = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="EUR")
    type = Column(Enum(TransactionType), nullable=False)
    description = Column(Text, nullable=True)
    # Can't delete an account if it has transactions associated with it
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="RESTRICT"))
    account = relationship("Account", back_populates="transactions")
    # Can't delete a category if it has transactions associated with it
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"))
    category = relationship("Category", back_populates="transactions")
    # Can't delete a person if he has transactions associated with him
    payer_person_id = Column(Integer, ForeignKey("people.id", ondelete="RESTRICT"))
    payer = relationship("Person", back_populates="transactions_paid")

    # If a transaction is deleted, all shares associated with it are deleted
    shares = relationship("TransactionShare", back_populates="transaction", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_tx_date_type', 'date', 'type'),
        CheckConstraint('amount_total > 0', name='ck_tx_amount_total_positive'),
    )

class TransactionShare(Base):
    __tablename__ = "transaction_shares"
    id = Column(Integer, primary_key=True, index=True)
    # If a transaction is deleted, all shares associated with it are deleted
    transaction_id = Column(Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction = relationship("Transaction", back_populates="shares")
    # A person can't be deleted if he has shares associated with him
    person_id = Column(Integer, ForeignKey("people.id", ondelete="RESTRICT"), nullable=False, index=True)
    person = relationship("Person", back_populates="shares")
    amount_share = Column(Float, nullable=False)
    source = Column(Enum(ShareSource), nullable=False, default=ShareSource.auto_default)
    
    __table_args__ = (
        UniqueConstraint("transaction_id", "person_id", name="uq_share_tx_person"),
        CheckConstraint("amount_share >= 0", name="ck_share_amount_non_negative"),
    )

class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    category = relationship("Category", back_populates="budgets")
    amount = Column(Float, nullable=False)