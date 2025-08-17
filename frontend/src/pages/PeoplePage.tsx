import React, { useEffect, useState } from 'react';
import { getPeople, createPerson, updatePerson, deletePerson } from '../api/people';
import Table, { Column } from '../components/Table';

export type Person = {
    id: number;
    name: string;
    is_me: boolean;
}

type PersonCreate = {
    name: string;
    is_me: boolean;
}

export default function PeoplePage() {
    const [people, setPeople] = useState<Person[]>([]);
    const [form, setForm] = useState<PersonCreate>({ name: "", is_me: false });

    const loadPeople = async () => {
        const data: Person[] = await getPeople();
        setPeople(data);
    }

    useEffect(() => {
        loadPeople();
    }, []);

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        await createPerson(form);
        setForm({ name: "", is_me: false });
        loadPeople();
    }

    const handleDeleteRow = async (row: Person) => {
        if (window.confirm("Are you sure you want to delete this person?")) {
            await deletePerson(row.id);
            loadPeople();
        }
    }

    const columns: Column<Person>[] = [
        { label: "ID", accessor: "id" },
        { label: "Name", accessor: "name" },
        { label: "Is Me", accessor: "is_me", Cell: (val) => (val ? "Yes" : "No") },
    ];

    return (
        <div>
            <h1 className="text-xl font-bold mb-4">People</h1>

            <form onSubmit={handleSubmit} className="mb-4 space-x-2">
                <input
                    type="text"
                    placeholder="Nombre"
                    className="border p-1"
                    value={form.name}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                        setForm({ ...form, name: e.target.value })
                    }
                />

                <label className="inline-flex items-center">
                    <input
                        type="checkbox"
                        className="mr-1"
                        checked={form.is_me}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                            setForm({ ...form, is_me: e.target.checked })
                        }
                    />
                    It's me
                </label>

                <button type="submit" className="bg-blue-600 text-white px-3 py-1 rounded">
                    Create
                </button>
            </form>

            <Table<Person> columns={columns} data={people} onDelete={handleDeleteRow} />
        </div>
    );
}