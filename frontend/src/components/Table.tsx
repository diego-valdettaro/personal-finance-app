import React, { useState, useMemo } from "react";
import { AgGridReact } from 'ag-grid-react';
import { ColDef, ModuleRegistry, AllCommunityModule } from 'ag-grid-community';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

// Register AG Grid modules
ModuleRegistry.registerModules([AllCommunityModule]);

export type Column<T, K extends keyof T = keyof T> = {
    label: string;
    accessor: K;
    Cell?: (value: T[K], row: T) => React.ReactNode;
    editable?: boolean;
    type?: 'text' | 'number' | 'select' | 'date';
    options?: { value: any; label: string }[];
};

export type TableProps<T> = {
    columns: Column<T>[];
    data: T[];
    onEdit?: (row: T) => void;
    onDelete?: (row: T) => void;
    onSave?: (row: T) => void;
    onCancel?: (row: T) => void;
    editingRow?: T | null;
}

export default function Table<T extends { id: number | string }>({
    columns, 
    data, 
    onDelete, 
    onSave, 
}: TableProps<T>) {
    const [selectedRows, setSelectedRows] = useState<T[]>([]);

    // Convert our column format to AG Grid column format
    const agGridColumns = useMemo((): ColDef[] => {
        return columns.map((col) => ({
            field: String(col.accessor),
            headerName: col.label,
            editable: col.editable,
            cellEditor: col.type === 'select' ? 'agSelectCellEditor' : undefined,
            cellEditorParams: col.type === 'select' ? {
                values: col.options?.map(opt => opt.value) || []
            } : undefined,
            cellRenderer: (params: any) => {
                const row = params.data;
                const value = row[col.accessor];

                if (col.type === 'select' && col.options) {
                    const option = col.options.find(opt => opt.value === value);
                    return option ? option.label : String(value);
                }

                return col.Cell ? col.Cell(value, row) : String(value);
            }
        }));
    }, [columns]);

    const defaultColDef = useMemo(() => ({
        sortable: true,
        filter: true,
        resizable: true,
        minWidth: 100,
        flex: 1,
    }), []);

    const onCellValueChanged = (params: any) => {
        if (onSave) {
            onSave(params.data);
        }
    };

    const onSelectionChanged = (params: any) => {
        setSelectedRows(params.api.getSelectedRows());
    };

    const handleDeleteSelected = () => {
        if (selectedRows.length > 0 && onDelete) {
            if (window.confirm(`Are you sure you want to delete ${selectedRows.length} selected item(s)?`)) {
                selectedRows.forEach(row => onDelete(row));
                setSelectedRows([]);
            }
        }
    };

    return (
        <div>
            {onDelete && selectedRows.length > 0 && (
                <div className="mb-4">
                    <button
                        onClick={handleDeleteSelected}
                        className="bg-gradient-to-r from-red-500 to-red-600 text-white px-6 py-3 rounded-lg hover:from-red-600 hover:to-red-700 transform hover:scale-105 transition-all duration-200 font-medium shadow-lg hover:shadow-xl flex items-center space-x-2"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                        <span>Delete Selected ({selectedRows.length})</span>    
                    </button>
                </div>
            )}
            
            <div className="ag-theme-alpine w-full" style={{ height: '500px' }}>
                {data.length === 0 ? (
                    <div className="flex items-center justify-center h-full text-gray-500">
                        No data available
                    </div>
                ) : (
                    <AgGridReact
                        columnDefs={agGridColumns}
                        rowData={data}
                        defaultColDef={defaultColDef}
                        onCellValueChanged={onCellValueChanged}
                        onSelectionChanged={onSelectionChanged}
                        rowSelection="multiple"
                        pagination={true}
                        paginationPageSize={10}
                        suppressCellFocus={true}
                    />
                )}
            </div>
        </div>
    );
}