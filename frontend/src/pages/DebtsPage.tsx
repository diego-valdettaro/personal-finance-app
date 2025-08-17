import React, { useEffect, useState } from "react";
import { getDebts } from "../api/reports";
import Table, { Column } from "../components/Table";

export type Debt = {
    id: number;
    person_name: string;
    debt: number;
    is_active: boolean;
};

export default function DebtsPage() {
    const [debts, setDebts] = useState<Debt[]>([]);

    useEffect(() => {
        (async () => {
            const data: Debt[] = await getDebts();
            setDebts(data);
        })();
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