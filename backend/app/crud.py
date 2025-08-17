from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException

# CRUD fucntions for Account
def get_accounts(db: Session):
    return db.query(models.Account).all()

def get_account(db: Session, account_id: int):
    return db.get(models.Account, account_id)

def create_account(db: Session, account: schemas.AccountCreate):
    db_account = models.Account(
        name=account.name,
        currency=account.currency,
        opening_balance=account.opening_balance
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def update_account(db: Session, account_id: int, account: schemas.AccountUpdate):
    db_account = get_account(db, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    for key, value in account.model_dump(exclude_unset=True).items():
        setattr(db_account, key, value)
    db.commit()
    db.refresh(db_account)
    return db_account

def delete_account(db: Session, account_id: int):
    db_account = get_account(db, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(db_account)
    db.commit()
    return db_account

# CRUD fucntions for Category
def get_categories(db: Session):
    return db.query(models.Category).all()

def get_category(db: Session, category_id: int):
    return db.get(models.Category, category_id)

def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(
        name=category.name,
        type=category.type
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def update_category(db: Session, category_id: int, category: schemas.CategoryUpdate):
    db_category = get_category(db, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in category.model_dump(exclude_unset=True).items():
        setattr(db_category, key, value)
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int):
    db_category = get_category(db, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(db_category)
    db.commit()
    return db_category

# CRUD fucntions for Person
def get_people(db: Session):
    return db.query(models.Person).all()

def get_person(db: Session, person_id: int):
    return db.get(models.Person, person_id)

def create_person(db: Session, person: schemas.PersonCreate):
    # Validate that there is only one "me"
    if person.is_me:
        if db.query(models.Person).filter(models.Person.is_me == True).count() > 0:
            raise HTTPException(status_code=400, detail="Only one 'me' person is allowed")
    db_person = models.Person(
        name=person.name,
        is_me=person.is_me
    )
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

def update_person(db: Session, person_id: int, person: schemas.PersonUpdate):
    db_person = get_person(db, person_id)
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    # If is_me is set to True, change the is_me of the other person to False
    if person.is_me:
        db.query(models.Person).filter(models.Person.id != person_id).update({"is_me": False})
    for key, value in person.model_dump(exclude_unset=True).items():
        setattr(db_person, key, value)
    db.commit()
    db.refresh(db_person)
    return db_person

def delete_person(db: Session, person_id: int):
    db_person = get_person(db, person_id)
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    # If the person is "me", raise an error
    if db_person.is_me:
        raise HTTPException(status_code=400, detail="Cannot delete the only 'me' person")
    db.delete(db_person)
    db.commit()
    return db_person

# CRUD fucntions for Transaction

# Helper function to replace the shares of a transaction
def _replace_shares(db: Session, db_transaction: models.Transaction, shares: list[schemas.TransactionShareCreate]):
    # Validate the sum of the shares is equal to the amount_total
    if sum(share.amount_share for share in shares) != db_transaction.amount_total:
        raise HTTPException(status_code=400, detail="The sum of the shares must be equal to the amount_total")
    # Delete all existing shares
    db.query(models.TransactionShare).filter(models.TransactionShare.transaction_id == db_transaction.id).delete()
    # Create new shares
    for share in shares:
        db_transaction.shares.append(models.TransactionShare(
            transaction_id=db_transaction.id,
            person_id=share.person_id,
            amount_share=share.amount_share,
            source=share.source
        ))
    db.add_all(db_transaction.shares)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transaction(db: Session, transaction_id: int):
    return db.get(models.Transaction, transaction_id)
    
def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    db_transaction = models.Transaction(
        date=transaction.date,
        amount_total=transaction.amount_total,
        currency=transaction.currency,
        type=transaction.type,
        description=transaction.description,
        account_id=transaction.account_id,
        category_id=transaction.category_id,
        payer_person_id=transaction.payer_person_id
    )
    db.add(db_transaction)

    # Create one share assigned to payer_person_id by default
    db_transaction.shares.append(models.TransactionShare(
        person_id=transaction.payer_person_id,
        amount_share=transaction.amount_total,
        source=models.ShareSource.auto_default
    ))

    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def split_transaction(db: Session, transaction_id: int, payer_person_id: int, shares: list[schemas.TransactionShareCreate]):
    db_transaction = get_transaction(db, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db_transaction.payer_person_id = payer_person_id
    _replace_shares(db, db_transaction, shares)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transactions(db: Session, **filters):
    query = db.query(models.Transaction)
    # Apply dynamic filters according to parameters
    if (date_from := filters.get("date_from")):
        query = query.filter(models.Transaction.date >= date_from)
    if (date_to := filters.get("date_to")):
        query = query.filter(models.Transaction.date <= date_to)
    if (account_id := filters.get("account_id")):
        query = query.filter(models.Transaction.account_id == account_id)
    if (category_id := filters.get("category_id")):
        query = query.filter(models.Transaction.category_id == category_id)
    if (person_id := filters.get("payer_person_id")):
        query = query.filter(models.Transaction.payer_person_id == person_id)
    return query.all()

def delete_transaction(db: Session, transaction_id: int):
    db_transaction = get_transaction(db, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(db_transaction)
    db.commit()
    return db_transaction

def update_transaction(db: Session, transaction_id: int, transaction: schemas.TransactionUpdate):
    db_transaction = get_transaction(db, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    for key, value in transaction.model_dump(exclude_unset=True).items():
        setattr(db_transaction, key, value)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

# CRUD functions for Report
def get_balances(db: Session):
    balances = []
    accounts = db.query(models.Account).all()
    for account in accounts:
        sum_incomes = db.query(models.Transaction).filter(models.Transaction.account_id == account.id, models.Transaction.type == models.TransactionType.income).scalar()
        sum_expenses = db.query(models.Transaction).filter(models.Transaction.account_id == account.id, models.Transaction.type == models.TransactionType.expense).scalar()
        balance = account.opening_balance + sum_incomes - sum_expenses
        balances.append(schemas.ReportBalance(
            account_id=account.id,
            account_name=account.name,
            balance=balance
        ))
    return balances

def get_debts(db: Session):
    debts = []
    people = db.query(models.Person).all()
    for person in people:
        # Get the sum of the transaction shares with the person_id where the transaction type is expense
        sum_debts = db.query(models.TransactionShare).filter(models.TransactionShare.person_id == person.id, models.Transaction.type == models.TransactionType.expense).scalar()
        sum_credits = db.query(models.TransactionShare).filter(models.TransactionShare.person_id == person.id, models.Transaction.type == models.TransactionType.income).scalar()
        debt = sum_debts - sum_credits
        debts.append(schemas.ReportDebt(
            person_id=person.id,
            person_name=person.name,
            debt=debt,
            is_active=debt != 0
        ))
    return debts

# CRUD fucntions for Budget

def get_budget(db: Session, id: int, month: int):
    return db.query(models.Budget).filter(models.Budget.id == id, models.Budget.month == month).first()

def get_annual_budget(db: Session, id: int):
    return db.query(models.Budget).filter(models.Budget.id == id).first()

def create_budget(db: Session, budget: schemas.BudgetCreate):
    db_budget = models.Budget(
        name=budget.name,
        year=budget.year,
        month=budget.month,
        category_id=budget.category_id,
        amount=budget.amount
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

def update_budget(db: Session, id: int, budget: schemas.BudgetUpdate):
    db_budget = get_annual_budget(db, id)
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    for key, value in budget.model_dump(exclude_unset=True).items():
        setattr(db_budget, key, value)
    db.commit()
    db.refresh(db_budget)
    return db_budget

def delete_budget(db: Session, id: int):
    db_budget = get_annual_budget(db, id)
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    db.delete(db_budget)
    db.commit()
    return

def get_budget_progress(db: Session, month: str):
    # Get the month and year from the month string
    month = int(month.split("-")[1])
    year = int(month.split("-")[0])
    # Get the budgets for the month
    budgets = db.query(models.Budget).filter(models.Budget.month == month, models.Budget.year == year).all()
    # Get the transactions for the month
    transactions = db.query(models.Transaction).filter(models.Transaction.date.month == month, models.Transaction.date.year == year).all()
    return budgets, transactions

