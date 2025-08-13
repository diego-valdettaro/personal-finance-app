import React, { useEffect, useMemo, useState } from 'react'
import { api } from '../api'
import type { Transaction, Category } from '../types'

type Editable = Pick<Transaction, 'id' | 'date' | 'amount' | 'category_id' | 'type' | 'currency' | 'description'>

export default function TransactionsTable({ refreshKey }: { refreshKey: number }) {
    
    const [items, setItems] = useState<Transaction[]>([])
    const [categories, setCategories] = useState<Category[]>([])
    // To manage state of the modal
    const [editing, setEditing] = useState<Editable | null>(null)
    const [saving, setSaving] = useState(false)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        api<Transaction[]>('/transactions/?limit=100').then(setItems)
        api<Category[]>('/categories/').then(setCategories)
    }, [refreshKey])

    const categoryNameById = useMemo(() => {
        return new Map(categories.map(c => [c.id, c.name]))
    }, [categories])

    async function onDelete(id: number) {
        if (!confirm('Do you want to permanently delete this transaction?')) return
        
        const prev = items
        setItems((xs) => xs.filter((x) => x.id !== id))

        try{
            await api<void>(`/transactions/${id}`, {method: 'DELETE'})
        } catch (e) {
            console.error(e)
            alert('Failed to delete. Restoring item.')
            setItems(prev)
        }
    }

    function onEdit(t: Transaction) {
        setError(null)

        const toYmd = (d: string) => {
            return d.length >= 10 ? d.slice(0, 10) : d
        }

        setEditing({
            id: t.id,
            date: toYmd(t.date),
            amount: t.amount,
            category_id: t.category_id,
            type: t.type,
            currency: t.currency,
            description: t.description ?? ''
        })
    }

    async function saveEdit() {
        if (!editing) return
        setSaving(true)
        setError(null)

        // Obligatory fields validation
        if (!editing.date || !editing.currency || !editing.type) {
            setError('Date, Type and Currency are required.')
            setSaving(false)
            return
        }
        
        // Modify locally before trying to make changes permanently
        const prev = items
        const optimistic = prev.map((x) => x.id === editing.id ? { ...x, ...editing} as Transaction : x)
        setItems(optimistic)

        try {
            const updated = await api<Transaction>(`/transactions/${editing.id}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(editing)
            })
            setItems((xs) => xs.map((x) => x.id === updated.id ? updated: x))
            setEditing(null)
        } catch (e: any) {
            console.error(e)
            setError('Failed to save changes. Please try again.')
            setItems(prev)
        } finally {
            setSaving(false)
        }
    }

    function cancelEdit() {
        setEditing(null)
        setError(null)
    }
    
    return (
        <div className="overflow-auto bg-white rounded-2xl shadow">
            <table className="min-w-full text-sm">
                <thead className="bg-gray-50">
                    <tr>
                        <th className="text-left p-2">Date</th>
                        <th className="text-left p-2">Amount</th>
                        <th className="text-left p-2">Category</th>
                        <th className="text-left p-2">Type</th>
                        <th className="text-left p-2">Currency</th>
                        <th className="text-left p-2">Description</th>
                        <th className="p-2">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {items.map((t) => (
                        <tr key={t.id} className="border-t">
                            <td className="p-2">{t.date}</td>
                            <td className="p-2">{t.amount.toFixed(2)}</td>
                            <td className="p-2">
                                {categoryNameById.get(t.category_id) ?? '-'}
                            </td>
                            <td className="p-2">{t.type}</td>
                            <td className="p-2">{t.currency}</td>
                            <td className="p-2">{t.description || ''}</td>
                            <td className="p-2 space-x-2">
                                <button onClick={() => onEdit(t)} className="underline">Edit</button>
                                <button onClick={() => onDelete(t.id)} className="underline text-red-600">Delete</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
            {/* Modal for editing transaction */}
            {editing && (
                <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
                    <div className="bg-white w-full max-w-lg rounded-2xl shadow-xl p-4 space-y-3">
                        <h2 className="text-lg font-semibold">Edit transaction</h2>

                        {error && <div className="text-red-600 text-sm">{error}</div>}

                        <div className="grid grid-cols-2 gap-3">
                            <label className="flex flex-col">
                                <span className="text-xs text-gray-600">Date</span>
                                <input
                                    type="date"
                                    className="border rounded-lg p-2"
                                    value={editing.date}
                                    onChange={e => setEditing({ ...editing, date: e.target.value })}
                                />
                            </label>

                        <label className="flex flex-col">
                            <span className="text-xs text-gray-600">Amount</span>
                            <input
                                type="number"
                                step="0.01"
                                className="border rounded-lg p-2"
                                value={editing.amount}
                                onChange={e => setEditing({ ...editing, amount: Number(e.target.value) })}
                            />
                        </label>

                        <label className="flex flex-col">
                            <span className="text-xs text-gray-600">Category</span>
                            <select
                                className="border rounded-lg p-2"
                                value={editing.category_id ?? ''}
                                onChange={e => setEditing({ ...editing, category_id: Number(e.target.value) })}
                            >
                                <option value="">-</option>
                                {categories.map(c => (
                                    <option key={c.id} value={c.id}>{c.name}</option>
                                ))}
                            </select>
                        </label>

                        <label className="flex flex-col">
                            <span className="text-xs text-gray-600">Type</span>
                            <select
                                className="border rounded-lg p-2"
                                value={editing.type}
                                onChange={e => setEditing({ ...editing, type: e.target.value as Transaction['type'] })}
                            >
                                <option value="expense">expense</option>
                                <option value="income">income</option>
                            </select>
                        </label>

                        <label className="flex flex-col">
                            <span className="text-xs text-gray-600">Currency</span>
                            <input
                                className="border rounded-lg p-2"
                                value={editing.currency}
                                onChange={e => setEditing({ ...editing, currency: e.target.value })}
                            />
                        </label>

                        <label className="flex flex-col col-span-2">
                            <span className="text-xs text-gray-600">Description</span>
                            <input
                                className="border rounded-lg p-2"
                                value={editing.description ?? ''}
                                onChange={e => setEditing({ ...editing, description: e.target.value })}
                            />
                        </label>
                        </div>

                        <div className="flex justify-end gap-2 pt-2">
                        <button
                            className="px-4 py-2 rounded-xl border"
                            onClick={cancelEdit}
                            disabled={saving}
                        >
                            Cancel
                        </button>
                        <button
                            className="px-4 py-2 rounded-xl bg-black text-white disabled:opacity-50"
                            onClick={saveEdit}
                            disabled={saving}
                        >
                            {saving ? 'Saving…' : 'Save'}
                        </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}