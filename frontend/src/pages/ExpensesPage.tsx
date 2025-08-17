import React, { useEffect, useState } from "react";
import { createTransaction } from "../api/transactions";
import { getAccounts } from "../api/accounts";
import { getCategories } from "../api/categories";
import { getPeople } from "../api/people";

type Account = {
    id: number;
    name: string;
    currency: string;
    opening_balance: number;
};

type Category = {
    id: number;
    name: string;
    type: "income" | "expense";
};

type Person = {
    id: number;
    name: string;
    is_me: boolean;
};

type ExpenseForm = {
    date: string;
    amount_total: number;
    currency: string;
    description: string;
    account_id: number | "";
    category_id: number | "";
    payer_person_id: number | "";
};

type TransactionCreateExpense = {
    date: string;
    amount_total: number;
    currency: string;
    description: string;
    account_id: number;
    category_id: number;
    payer_person_id: number;
    type: "expense";	
};

export default function ExpensesPage() {
    const [accounts, setAccounts] = useState<Account[]>([]);
    const [categories, setCategories] = useState<Category[]>([]);
    const [people, setPeople] = useState<Person[]>([]);
    const [form, setForm] = useState<ExpenseForm>({
        date: "",
        amount_total: 0,
        currency: "",
        description: "",
        account_id: "",
        category_id: "",
        payer_person_id: "",
    });

    useEffect(() => {
        (async () => {
            const [accounts, categories, people] = await Promise.all([
                getAccounts() as Promise<Account[]>,
                getCategories() as Promise<Category[]>,
                getPeople() as Promise<Person[]>,
            ]);
            setAccounts(accounts);
            setCategories(categories);
            setPeople(people);
        })();
    }, []);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        if (form.account_id === "" || form.category_id === "" || form.payer_person_id === "") {
            alert("Please select an account, category, and payer person");
            return;
        }

        const payload: TransactionCreateExpense = {
            date: form.date,
            amount_total: form.amount_total,
            currency: form.currency,
            description: form.description,
            account_id: Number(form.account_id),
            category_id: Number(form.category_id),
            payer_person_id: Number(form.payer_person_id),
            type: "expense",
        };

        await createTransaction(payload);
        alert("Expense created successfully");

        setForm({
            date: "",
            amount_total: 0,
            currency: "",
            description: "",
            account_id: "",
            category_id: "",
            payer_person_id: "",
        });
    };

    return (
        <div>
          <h1 className="text-xl font-bold mb-4">Expenses</h1>
    
          <form onSubmit={handleSubmit} className="space-y-2">
            <input
              type="date"
              className="border p-1 block"
              placeholder="Date"
              value={form.date}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setForm({ ...form, date: e.target.value })
              }
            />
    
            <input
              type="number"
              step="0.01"
              className="border p-1 block"
              placeholder="Amount"
              value={form.amount_total}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setForm({ ...form, amount_total: parseFloat(e.target.value) || 0 })
              }
            />
    
            <input
              type="text"
              className="border p-1 block"
              placeholder="Currency"
              value={form.currency}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setForm({ ...form, currency: e.target.value })
              }
            />
    
            <input
              type="text"
              className="border p-1 block"
              placeholder="Description"
              value={form.description}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setForm({ ...form, description: e.target.value })
              }
            />
    
            <select
              className="border p-1 block"
              value={form.account_id}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                setForm({...form, account_id: e.target.value === "" ? "" : Number(e.target.value)})
              }
            >
              <option value="">Account</option>
              {accounts.map((acc) => (
                <option key={acc.id} value={acc.id}>
                  {acc.name}
                </option>
              ))}
            </select>
    
            <select
              className="border p-1 block"
              value={form.category_id}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                setForm({ ...form, category_id: e.target.value === "" ? "" : Number(e.target.value)})
              }
            >
              <option value="">Category</option>
              {categories
                .filter((c) => c.type === "expense")
                .map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
            </select>
    
            <select
              className="border p-1 block"
              value={form.payer_person_id}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                setForm({ ...form, payer_person_id: e.target.value === "" ? "" : Number(e.target.value)})
              }
            >
              <option value="">Payer</option>
              {people.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
    
            <button type="submit" className="bg-blue-600 text-white px-3 py-1 rounded">
              Register
            </button>
          </form>
        </div>
      );
    }

