import React, { useEffect, useState, useMemo } from "react";
import { getTransactions, getTransaction, deleteTransaction, updateTransaction, splitTransaction } from "../api/transactions";
import { getPeople } from "../api/people";
import { getCategories } from "../api/categories";
import { getAccounts } from "../api/accounts";
import Table, { Column } from "../components/Table";
import SplitModal from "../components/SplitModal";
import { Transaction, TransactionFilters, Person, SplitPayload, Category, Account } from "../types";

export default function TransactionsPage() {
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [filters, setFilters] = useState<TransactionFilters>({});
    const [people, setPeople] = useState<Person[]>([]);
    const [categories, setCategories] = useState<Category[]>([]);
    const [accounts, setAccounts] = useState<Account[]>([]);
    const [showSplitModal, setShowSplitModal] = useState(false);
    const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);
    const [editingTransaction, setEditingTransaction] = useState<Transaction | null>(null);
    
    useEffect(() => {
        getTransactions(filters).then((response) => setTransactions(response))
        getPeople().then((response) => setPeople(response))
        getCategories().then((response) => setCategories(response))
        getAccounts().then((response) => setAccounts(response))
    }, []);
    
    // Create a mapping for category names
    const categoryNameById = useMemo<Map<Category["id"], Category["name"]>>(() => {
        return new Map(categories.map(c => [c.id, c.name]))
    }, [categories]);

    // Create a mapping for account names
    const accountNameById = useMemo<Map<Account["id"], Account["name"]>>(() => {
        return new Map(accounts.map(a => [a.id, a.name]))
    }, [accounts]);

    const handleDeleteRow = async (row: Transaction) => {
        if (window.confirm("Are you sure you want to delete this transaction?")) {
            await deleteTransaction(row.id);
            getTransactions(filters).then((response) => setTransactions(response))
        }
    };

    const handleEditRow = (row: Transaction) => {
        setEditingTransaction(row);
    };

    const handleSaveRow = async (updatedTransaction: Transaction) => {
        try {
            await updateTransaction(updatedTransaction.id, updatedTransaction);
            setEditingTransaction(null);
            getTransactions(filters).then((response) => setTransactions(response));
        } catch (error) {
            console.error('Error updating transaction:', error);
        }
    };

    const handleCancelEdit = (row: Transaction) => {
        setEditingTransaction(null);
    };
    
    const handleOpenSplitModal = (row: Transaction) => {
        setSelectedTransaction(row);
        setShowSplitModal(true);
    };

    const handleSaveSplitModal = async (payload: SplitPayload) => {
        if (!selectedTransaction) {
            return;
        }
        await splitTransaction(selectedTransaction.id, payload);
        setShowSplitModal(false);
        setSelectedTransaction(null);
        getTransactions(filters).then((response) => setTransactions(response))
    };

    const columns: Column<Transaction>[] = [
        { 
            label: "Amount", 
            accessor: "amount_total", 
            editable: true, 
            type: "number" 
        },
        { 
            label: "Date", 
            accessor: "date", 
            editable: true, 
            type: "date" 
        },
        { 
            label: "Category", 
            accessor: "category_id",
            editable: true,
            type: "select",
            options: categories.map(c => ({ value: c.id, label: c.name })),
            Cell: (value: string | number | undefined) => {
                if (typeof value === 'number') {
                    return categoryNameById.get(value) ?? `Unknown (${value})`;
                }
                return value || 'N/A';
            }
        },
        { 
            label: "Account", 
            accessor: "account_id",
            editable: true,
            type: "select",
            options: accounts.map(a => ({ value: a.id, label: a.name })),
            Cell: (value: string | number | undefined) => {
                if (typeof value === 'number') {
                    return accountNameById.get(value) ?? `Unknown (${value})`;
                }
                return value || 'N/A';
            }
        },
        { 
            label: "Currency", 
            accessor: "currency", 
            editable: true, 
            type: "text" 
        },
        { 
            label: "Description", 
            accessor: "description", 
            editable: true, 
            type: "text" 
        },
    ];

    return (
        <div>
          <h1 className="text-xl font-bold mb-4">Transactions</h1>
          <Table<Transaction>
            columns={columns}
            data={transactions}
            onDelete={handleDeleteRow}
            onEdit={handleEditRow}
            onSave={handleSaveRow}
            onCancel={handleCancelEdit}
            editingRow={editingTransaction}
          />
    
          {(showSplitModal && selectedTransaction) && (
            <SplitModal
              transaction={{
                amount_total: selectedTransaction.amount_total,
                payer_person_id: selectedTransaction.payer_person_id,
              }}
              people={people}
              onSave={handleSaveSplitModal}
              onClose={() => {
                setShowSplitModal(false);
                setSelectedTransaction(null);
              }}
            />
          )}
        </div>
      );
    }