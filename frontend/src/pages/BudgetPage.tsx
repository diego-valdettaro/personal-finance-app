import React, { useState } from "react";
import { getBudgetProgress } from "../api/reports";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";

type BudgetRow = {
    category_name: string;
    budget: number;
    actual: number;
}

export default function BudgetPage() {
    const [month, setMonth] = useState<string>("");
    const [data, setData] = useState<BudgetRow[]>([]);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const progress = (await getBudgetProgress(month)) as BudgetRow[];
        setData(progress);
    }

    return (
        <div>
            <h1 className="text-xl font-bold mb-4">Budget</h1>

            <form onSubmit={handleSubmit} className="mb-4">
                <input
                    type="month"
                    value={month}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                        setMonth(e.target.value)
                    }
                    className="border p-1"
                />
                <button
                    type="submit"
                    className="bg-blue-600 text-white px-3 py-1 rounded ml-2"
                >
                    Search
                </button>
            </form>

            {data.length > 0 && (
                <BarChart
                    width={500}
                    height={300}
                    data={data}
                    margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="category" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="budget" name="Presupuesto" fill="#8884d8" />
                    <Bar dataKey="actual" name="Real" fill="#82ca9d" />
                </BarChart>
            )}
        </div>
    );
}
