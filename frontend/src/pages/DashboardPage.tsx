import React, { useEffect, useState } from "react";
import { getBalances } from "../api/reports";
import Card from "../components/Card";

type BalanceRow = {
    id?: number | string;
    account_name?: string;
    balance: number;
}

export default function DashboardPage() {
    const [balances, setBalances] = useState<BalanceRow[]>([]);

    useEffect(() => {
        (async () => {
            const data: BalanceRow[] = await getBalances();
            setBalances(data);
        })();
    }, []);

    const totalBalance = balances.reduce((sum, b) => sum + Number(b.balance), 0);

    return (
        <div className="space-y-4">
            <h1 className="text-xl font-bold mb-4">Dashboard</h1>
    
            <div className="grid md:grid-cols-3 gap-4">
                <Card title="Total Balance" value={totalBalance.toFixed(2)} />
            </div>
        </div>
      );
    }