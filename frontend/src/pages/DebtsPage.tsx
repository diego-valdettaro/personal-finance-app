import React, { useEffect, useState } from "react";
import { getDebts } from "../api/reports";
import Table, { Column } from "../components/Table";
import { Debt } from "../types";

export default function DebtsPage() {
    const [debts, setDebts] = useState<Debt[]>([]);

    useEffect(() => {
        getDebts().then((response) => setDebts(response))
    }, []);

    const columns: Column<Debt>[] = [
        {
            label: "Person", accessor: "person_name",
        },
        {
            label: "Debt", accessor: "debt",
        },
        {
            label: "Active", accessor: "is_active",
        },
    ];

    return (
        <div>
            <h1 className="text-xl font-bold mb-4">Debts</h1>
            <Table columns={columns} data={debts} />
        </div>
    );
}