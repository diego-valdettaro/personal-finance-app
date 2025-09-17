"""
CRUD operations package.
"""

# Import all CRUD modules
from . import users, people, accounts, transactions, postings, splits, fx_rates, budgets, reports, common

# Re-export commonly used functions for backward compatibility
from .users import (
    get_users, get_user, get_user_any_status, create_user, update_user, 
    deactivate_user, activate_user
)

from .people import (
    get_people, get_person, get_person_any_status,
    create_person, update_person, deactivate_person, activate_person
)

from .accounts import (
    get_accounts, get_account, get_account_any_status, create_account, 
    update_account, deactivate_account, activate_account
)

from .transactions import (
    get_transactions, get_transaction, create_transaction, update_transaction,
    deactivate_transaction, activate_transaction
)

from .postings import get_postings, get_posting

from .splits import get_splits, get_split

from .fx_rates import (
    get_fx_rate_by_id, get_fx_rate_by_key, create_fx_rate, update_fx_rate_by_key
)

from .budgets import (
    get_budget_month, get_budget, create_budget, update_budget, delete_budget
)

from .reports import (
    get_balances, get_debts, get_monthly_budget_progress
)

__all__ = [
    # Users
    "get_users", "get_user", "get_user_any_status", "create_user", "update_user", 
    "deactivate_user", "activate_user",
    
    # People
    "get_people", "get_person", "get_person_any_status",
    "create_person", "update_person", "deactivate_person", "activate_person",
    
    # Accounts
    "get_accounts", "get_account", "get_account_any_status", "create_account", 
    "update_account", "deactivate_account", "activate_account",
    
    # Transactions
    "get_transactions", "get_transaction", "create_transaction", "update_transaction",
    "deactivate_transaction", "activate_transaction",
    
    # Postings
    "get_postings", "get_posting",
    
    # Splits
    "get_splits", "get_split",
    
    # FX Rates
    "get_fx_rate_by_id", "get_fx_rate_by_key", "create_fx_rate", "update_fx_rate_by_key",
    
    # Budgets
    "get_budget_month", "get_budget", "create_budget", "update_budget", "delete_budget",
    
    # Reports
    "get_balances", "get_debts", "get_monthly_budget_progress",
    
    # Modules
    "users", "people", "accounts", "transactions", "postings", "splits", 
    "fx_rates", "budgets", "reports", "common"
]
