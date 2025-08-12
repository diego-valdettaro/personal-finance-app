import React, { useState } from 'react'
import TransactionForm from './components/TransactionForm'
import TransactionsTable from './components/TransactionsTable'

export default function App() {
    
    const [refreshKey, setRefreshKey] = useState(0)

    return (
        <div className="min-h-screen bg-gray-100">
            <div className="max-w-5xl mx-auto p-6 space-y-6">
                <header className="flex items-center justify-between">
                    <h1 className="text-2xl font-bold">Mis Finanzas (MVP)</h1>
                </header>
                <TransactionForm onCreated={() => setRefreshKey((k) => k + 1)} />
                <TransactionsTable refreshKey={refreshKey} />
            </div>
        </div>
    )
}