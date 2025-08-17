import React, { useEffect, useState } from "react";
import { getTransactions, getTransaction, deleteTransaction, updateTransaction, splitTransaction } from "../api/transactions";
import { getPeople } from "../api/people";
import Table, { Column } from "../components/Table";
import SplitModal from "../components/SplitModal";

export type Person = {
    id: number;
    name: string;
    is_me: boolean;
};

export type Transaction = {
    id: number;
    date: string;
    description?: string | null;
    amount_total: number;
    account_id: number;
    category_id: number;
    payer_person_id: number;
};

export type TransactionFilters = Partial<{
    date_from: string;
    date_to: string;
    account_id: number;
    category_id: number;
    payer_person_id: number;
}>;

export type SplitPayload = {
    payer_person_id: number;
    shares: {
        person_id: number;
        amount: number;
        source: "user_manual";
    }[];
};

export default function TransactionsPage() {
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [filters, setFilters] = useState<TransactionFilters>({});
    const [people, setPeople] = useState<Person[]>([]);
    const [showSplitModal, setShowSplitModal] = useState(false);
    const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);

    const loadTransactions = async () => {
        const data: Transaction[] = await getTransactions(filters);
        setTransactions(data);
    };

    const loadPeople = async () => {
        const data: Person[] = await getPeople();
        setPeople(data);
    };
    
    useEffect(() => {
        loadTransactions();
        loadPeople();
    }, []);

    const handleDeleteRow = async (row: Transaction) => {
        if (window.confirm("Are you sure you want to delete this transaction?")) {
            await deleteTransaction(row.id);
            loadTransactions();
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
        loadTransactions();
    };

    const columns: Column<Transaction>[] = [
        { label: "Date", accessor: "date" },
        { label: "Account", accessor: "account_id" },
        { label: "Category", accessor: "category_id" },
        { label: "Payer", accessor: "payer_person_id" },
        { label: "Amount", accessor: "amount_total" },
        { label: "Description", accessor: "description" },
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