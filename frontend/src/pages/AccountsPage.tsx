import React, { useEffect, useState } from 'react';
import { getAccounts, createAccount, updateAccount, deleteAccount } from '../api/accounts';
import Table, { Column } from '../components/Table';
import { Account, AccountCreate } from '../types';

export default function AccountsPage() {
    const [accounts, setAccounts] = useState<Account[]>([]);
    const [form, setForm] = useState<AccountCreate>({
        name: "",
        currency: "",
        opening_balance: 0,
    });
    const [editingAccount, setEditingAccount] = useState<Account | null>(null);

    useEffect(() => {
        getAccounts().then((response) => setAccounts(response))
        console.log(accounts)
    }, []);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        await createAccount(form);
        setForm({ name: "", currency: "", opening_balance: 0 });
        getAccounts().then((response) => setAccounts(response))
    }

    const handleDeleteRow = async (row: Account) => {
        if (window.confirm("Are you sure you want to delete this account?")) {
            await deleteAccount(row.id);
            getAccounts().then((response) => setAccounts(response))
        }
    };

    const handleEditRow = (row: Account) => {
        setEditingAccount(row);
    };

    const handleSaveRow = async (updatedAccount: Account) => {
        await updateAccount(updatedAccount.id, updatedAccount);
        setEditingAccount(null);
        getAccounts().then((response) => setAccounts(response));
    };

    const handleCancelEdit = (row: Account) => {
        setEditingAccount(null);
    };

    const columns: Column<Account>[] = [
        { label: "ID", accessor: "id" },
        { 
            label: "Name", 
            accessor: "name", 
            editable: true, 
            type: "text" 
        },
        { 
            label: "Currency", 
            accessor: "currency", 
            editable: true, 
            type: "select",
            options: [
                { value: "EUR", label: "EUR" },
                { value: "USD", label: "USD" },
                { value: "PEN", label: "PEN" }
            ]
        },
        { 
            label: "Opening Balance", 
            accessor: "opening_balance", 
            editable: true, 
            type: "number" 
        },
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
    
            <select
              className="border p-1"
              value={form.currency}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                setForm({ ...form, currency: e.target.value })
              }
            >
              <option value="">Select Currency</option>
              <option value="EUR">EUR</option>
              <option value="USD">USD</option>
              <option value="PEN">PEN</option>
            </select>
    
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
              className="bg-green-600 text-white px-3 py-1 rounded"
            >
              Create Account
            </button>
          </form>
    
          <Table<Account>
            columns={columns}
            data={accounts}
            onEdit={handleEditRow}
            onSave={handleSaveRow}
            onCancel={handleCancelEdit}
            editingRow={editingAccount}
            onDelete={handleDeleteRow}
          />
        </div>
      );
    }