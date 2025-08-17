import React from "react";


export type Column<T, K extends keyof T = keyof T> = {
    label: string;
    accessor: K ;
    Cell?: (value: T[K], row: T) => React.ReactNode;
  };

export type TableProps<T> = {
    columns: Column<T>[];
    data: T[];
    onEdit?: (row: T) => void;
    onDelete?: (row: T) => void;
}

export default function Table<T extends { id: number | string }>({columns, data, onEdit, onDelete}: TableProps<T>) {
    return (
        <table className="min-w-full text-left border-collapse">
            <thead>
                <tr>
                    {columns.map((col) => (
                        <th key={String(col.accessor)} className="px-4 py-2 border-b bg-gray-50">
                            {col.label}
                        </th>
                    ))}
                    {(onEdit || onDelete) && <th className="px-4 py-2 border-b bg-gray-50">Actions</th>}
                </tr>
            </thead>
            <tbody>
                {data.map((row) => (
                    <tr key={row.id} className="border-b hover:bg-gray-50">
                        {columns.map((col) => (
                            <td key={String(col.accessor)} className="px-4 py-2">
                                {col.Cell ? col.Cell(row[col.accessor], row) : String(row[col.accessor])}
                            </td>
                        ))}
                        {(onEdit || onDelete) && (
                            <td className="px-4 py-2 space-x-2">
                                {onEdit && <button onClick={() => onEdit(row)} className="text-blue-600">Edit</button>}
                                {onDelete && <button onClick={() => onDelete(row)} className="text-red-600">Delete</button>}
                            </td>
                        )}
                    </tr>
                ))}
            </tbody>
        </table>
    );
}