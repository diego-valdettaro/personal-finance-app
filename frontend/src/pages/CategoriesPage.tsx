import React, { useEffect, useState } from 'react';
import { getCategories, createCategory, updateCategory, deleteCategory } from '../api/categories';
import Table, { Column } from '../components/Table';
import { Category, CategoryCreate } from '../types';

export default function CategoriesPage() {
    const [categories, setCategories] = useState<Category[]>([]);
    const [form, setForm] = useState<CategoryCreate>({
        name: "",
        type: "expense",
    });

    useEffect(() => {
        getCategories().then((response) => setCategories(response))
    }, []);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        await createCategory(form);
        setForm({ name: "", type: "expense" });
        getCategories().then((response) => setCategories(response))
    }

    const handleDeleteRow = async (row: Category) => {
        if (window.confirm("Are you sure you want to delete this category?")) {
            await deleteCategory(row.id);
            getCategories().then((response) => setCategories(response))
        }
    }
    
    const columns: Column<Category>[] = [
        { label: "ID", accessor: "id" },
        { label: "Name", accessor: "name" },
        { label: "Type", accessor: "type" },
    ];

    return (
        <div>
            <h1 className="text-xl font-bold mb-4">Categories</h1>
            <form onSubmit={handleSubmit} className="mb-4 space-x-2">
                <input
                type="text"
                placeholder="Name"
                className="border p-1"
                value={form.name}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    setForm({ ...form, name: e.target.value })
                }
                />

                <select 
                className="border p-1"
                value={form.type}
                onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                    setForm({ ...form, type: e.target.value as CategoryCreate["type"] })
                }
                >
                    <option value="income">Income</option>
                    <option value="expense">Expense</option>
                </select>

                <button type="submit" className="bg-blue-600 text-white px-3 py-1 rounded">
                    Create
                </button>
            </form>

            <Table<Category> columns={columns} data={categories} onDelete={handleDeleteRow} />
    </div>
    )
}