import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import DashboardPage from './pages/DashboardPage';
import ManagementPage from './pages/ManagementPage';
import TransactionsPage from './pages/TransactionsPage';
import ExpensesPage from './pages/ExpensesPage';
import DebtsPage from './pages/DebtsPage';
import BudgetPage from './pages/BudgetPage';

export default function App() {
    return (
        <Routes>
            <Route path="/" element={<Layout />}>
                <Route index element={<Navigate to="/dashboard" />} />
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="management" element={<ManagementPage />} />
                <Route path="transactions" element={<TransactionsPage />} />
                <Route path="expenses" element={<ExpensesPage />} />
                <Route path="debts" element={<DebtsPage />} />
                <Route path="budget" element={<BudgetPage />} />
            </Route>
            <Route path="*" element={<Navigate to="/dashboard" />} />
        </Routes>
    );
}