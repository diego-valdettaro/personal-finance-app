import React, { useEffect, useState } from 'react';
import { getAccounts, createAccount, updateAccount, deleteAccount } from '../api/accounts';
import Table, { Column } from '../components/Table';

// Define types
export type Account = {
    id: number;
    name: string;
    currency: string;
    opening_balance: number;
};

type AccountCreate = {
    name: string;
    currency: string;
    opening_balance: number;
};

export default function AccountsPage() {
    const [accounts, setAccounts] = useState<Account[]>([]);
    const [form, setForm] = useState<AccountCreate>({
        name: "",
        currency: "",
        opening_balance: 0,
    });
    
    const loadAccounts = async () => {
        const data: Account[] = await getAccounts();
        setAccounts(data)
    }

    useEffect(() => {
        loadAccounts();
    }, []);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        await createAccount(form);
        setForm({ name: "", currency: "", opening_balance: 0 });
        loadAccounts();
    }

    const handleDeleteRow = async (row: Account) => {
        if (window.confirm("Are you sure you want to delete this account?")) {
            await deleteAccount(row.id);
            loadAccounts();
        }
    };

    const columns: Column<Account>[] = [
        { label: "ID", accessor: "id" },
        { label: "Name", accessor: "name" },
        { label: "Currency", accessor: "currency" },
        { label: "Opening Balance", accessor: "opening_balance" },
    ];

    return (
        <div>
          <h1 className="text-xl font-bold mb-4">Accounts</h1>
    
          <form onSubmit={handleSubmit} className="mb-4 space-x-2">
            <input
              type="text"
              placeholder="Nombre"
              className="border p-1"
              value={form.name}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setForm({ ...form, name: e.target.value })
              }
            />
    
            <input
              type="text"
              placeholder="Moneda"
              className="border p-1"
              value={form.currency}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setForm({ ...form, currency: e.target.value })
              }
            />
    
            <input
              type="number"
              step="0.01"
              placeholder="Saldo inicial"
              className="border p-1"
              value={form.opening_balance}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setForm({
                  ...form,
                  opening_balance: parseFloat(e.target.value) || 0,
                })
              }
            />
    
            <button
              type="submit"
              className="bg-blue-600 text-white px-3 py-1 rounded"
            >
              Crear
            </button>
          </form>
    
          <Table<Account>
            columns={columns}
            data={accounts}
            onDelete={handleDeleteRow}
          />
        </div>
      );
    }