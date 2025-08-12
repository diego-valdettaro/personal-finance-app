import React, { useEffect, useState } from 'react'
import { api } from '../api'
import type { Transaction } from '../types'

export default function TransactionsTable({ refreshKey }: { refreshKey: number }) {
    
    const [items, setItems] = useState<Transaction[]>([])

    useEffect(() => {
        api<Transaction[]>('/transactions/?limit=100').then(setItems)
    }, [refreshKey])

    return (
        <div className="overflow-auto bg-white rounded-2xl shadow">
            <table className="min-w-full text-sm">
                <thead className="bg-gray-50">
                    <tr>
                        <th className="text-left p-2">Fecha</th>
                        <th className="text-right p-2">Monto</th>
                        <th className="text-left p-2">Tipo</th>
                        <th className="text-left p-2">Moneda</th>
                        <th className="text-left p-2">Descripción</th>
                    </tr>
                </thead>
                <tbody>
                    {items.map((t) => (
                        <tr key={t.id} className="border-t">
                            <td className="p-2">{t.date}</td>
                            <td className="p-2 text-right">{t.amount.toFixed(2)}</td>
                            <td className="p-2">{t.type}</td>
                            <td className="p-2">{t.currency}</td>
                            <td className="p-2">{t.description || ''}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}