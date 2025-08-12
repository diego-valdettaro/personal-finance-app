from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    currency = Column(String(3), nullable=False, default="EUR")
    transactions = relationship("Transaction", back_populates="account")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    type = Column(String(10), nullable=False, default="expense")
    transactions = relationship("Transaction", back_populates="category")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="EUR")
    type = Column(String(10), nullable=False)
    description = Column(Text, nullable=True)
    detail_json = Column(Text, nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
