import React, { useEffect, useState } from 'react'
import { api } from '../api'
import type { Account, Category } from '../types'
import { toProperCase } from '../utils/string'

type Props = { onCreated: () => void }

export default function TransactionForm({ onCreated }: Props){
    // Accounts and Categories state in form, which will be lists of predefined types
    // They receive en empty list as a initial value
    const [accounts, setAccounts] = useState<Account[]>([])
    const [categories, setCategories] = useState<Category[]>([])
    // Not necessary to explicitly say it's a type Transaction in this case
    const [form, setForm] = useState({
        date: new Date().toISOString().slice(0,10),
        amount: 0,
        currency: 'EUR',
        type: 'expense' as 'income' | 'expense',
        description: '',
        account_id: 0,
        category_id: 0,
    })

    // Call the backend api and populate Accounts and Categories lists
    useEffect(() => {
        api<Account[]>('/accounts/').then(setAccounts)
        api<Category[]>('/categories/').then(setCategories)
    }, [])

    // Function to handle a change in value of inputs or selects
    function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) {
        const {name, value} = e.target
        // Call setForm function to modify the form
        setForm((f) => ({
            ...f, 
            // Ensure numeric type for amount
            ...(name === 'amount' ? { amount: Number(value) } : {}),

            // Ensure numeric type for select IDs (HTML select returns strings)
            ...(name === 'account_id' ? { account_id: Number(value) } : {}),
            ...(name === 'category_id' ? { category_id: Number(value) } : {}),

            // Generic fallback: assign raw value
            ...(name !== 'amount' && name !== 'account_id' && name !== 'category_id' ? { [name]: value } : {}),
        }))
    }

    // Function to handle the form submit
    async function handleSubmit(e: React.FormEvent) {
        // Prevents page reload
        e.preventDefault()

        // Send the form as JSON to the backend
        await api('/transactions/', { method: 'POST', body: JSON.stringify(form) })

        // Soft reset: keep date, type, currency, account/category; clear amount & description
        setForm((f) => ({ ...f, amount: 0, description: ''}))
        // Inform the parent to refresh list or counters
        onCreated()
    }

    return (
        <form onSubmit={handleSubmit} className="space-y-3 p-4 bg-white rounded-2xl shadow">
            <div className="grid grid-cols-2 gap-3">
                <label className="flex flex-col">
                    <span className="text-sm">Fecha</span>
                    <input name="date" type="date" value={form.date} onChange={handleChange} className="border rounded px-2 py-1" required />
                </label>
                <label className="flex flex-col">
                    <span className="text-sm">Monto</span>
                    <input name="amount" type="number" step="0.01" value={form.amount} onChange={handleChange} className="border rounded px-2 py-1" required />
                </label>
                <label className="flex flex-col">
                    <span className="text-sm">Tipo</span>
                    <select name="type" value={form.type} onChange={handleChange} className="border rounded px-2 py-1" required >
                        <option value="expense">Gasto</option>
                        <option value="income">Ingreso</option>
                    </select>
                </label>
                <label className="flex flex-col">
                    <span className="text-sm">Moneda</span>
                    <input name="currency" value={form.currency} onChange={handleChange} className="border rounded px-2 py-1" required />
                </label>
                <label className="flex flex-col col-span-2">
                    <span className="text-sm">Descripción</span>
                    <input name="description" value={form.description} onChange={handleChange} className="border rounded px-2 py-1" />
                </label>
                <label className="flex flex-col">
                    <span className="text-sm">Cuenta</span>
                    <select name="account_id" value={form.account_id} onChange={handleChange} className="border rounded px-2 py-1">
                        <option value={0}>Selecciona…</option>
                        {accounts.map((a) => (
                            <option key={a.id} value={a.id}>
                                {a.name} ({a.currency})
                            </option>
                        ))}
                    </select>
                </label>
                <label className="flex flex-col">
                    <span className="text-sm">Categoría</span>
                    <select name="category_id" value={form.category_id} onChange={handleChange} className="border rounded px-2 py-1">
                        <option value={0}>Selecciona…</option>
                            {categories.map((c) => (
                                <option key={c.id} value={c.id}>
                                    {toProperCase(c.name)}
                                </option>
                            ))}
                    </select>
                </label>
            </div>
            <button type="submit" className="px-3 py-2 rounded-xl bg-black text-white">Agregar</button>
        </form>
    )
}
