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

    const accountNameById = useMemo<Map<Account["id"], Account["name"]>>(() => {
        return new Map(accounts.map(a => [a.id, a.name]))
    }, [accounts]);

    const payerNameById = useMemo<Map<Person["id"], Person["name"]>>(() => {
        return new Map(people.map(p => [p.id, p.name]))
    }, [people]);

    const loadPeople = async () => {
        const data: Person[] = await getPeople();
        setPeople(data);
};

    const handleDeleteRow = async (row: Transaction) => {
        if (window.confirm("Are you sure you want to delete this transaction?")) {
            await deleteTransaction(row.id);
            getTransactions(filters).then((response) => setTransactions(response))
        }
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
        { label: "Amount", accessor: "amount_total" },
        { label: "Date", accessor: "date" },
        { 
            label: "Category", 
            accessor: "category_id",
            Cell: (value: number) => categoryNameById.get(value) ?? `Unknown (${value})`
        },
        { 
            label: "Account", 
            accessor: "account_id",
            Cell: (value: number) => accountNameById.get(value) ?? `Unknown (${value})`
        },
        { label: "Currency", accessor: "currency" },
        { label: "Description", accessor: "description" },
        { 
            label: "Payer", 
            accessor: "payer_person_id",
            Cell: (value: number) => payerNameById.get(value) ?? `Unknown (${value})`
        },
    ];

    return (
        <div>
          <h1 className="text-xl font-bold mb-4">Transactions</h1>
          <Table<Transaction>
            columns={columns}
            data={transactions}
            onDelete={handleDeleteRow}
            onEdit={handleOpenSplitModal}
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