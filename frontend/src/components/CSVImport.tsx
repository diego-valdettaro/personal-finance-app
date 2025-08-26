import React, { useState } from 'react';
import { Account, Category, Person, TransactionCreateExpense } from '../types';

interface CSVImportProps {
    accounts: Account[];
    categories: Category[];
    people: Person[];
    onImport: (transactions: TransactionCreateExpense[]) => Promise<void>;
}

interface CSVRow {
    date: string;
    amount: string;
    currency: string;
    description: string;
    account: string;
    category: string;
    payer: string;
}

export default function CSVImport({ accounts, categories, people, onImport }: CSVImportProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [csvData, setCsvData] = useState<string>('');
    const [isProcessing, setIsProcessing] = useState(false);
    const [previewData, setPreviewData] = useState<CSVRow[]>([]);
    const [errors, setErrors] = useState<string[]>([]);

    const parseCSV = (csvText: string): CSVRow[] => {
        const lines = csvText.trim().split('\n');
        const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
        
        // Expected headers
        const expectedHeaders = ['date', 'amount', 'currency', 'description', 'account', 'category', 'payer'];
        
        // Validate headers
        const missingHeaders = expectedHeaders.filter(h => !headers.includes(h));
        if (missingHeaders.length > 0) {
            throw new Error(`Missing required headers: ${missingHeaders.join(', ')}`);
        }

        return lines.slice(1).map((line, index) => {
            const values = line.split(',').map(v => v.trim());
            return {
                date: values[headers.indexOf('date')] || '',
                amount: values[headers.indexOf('amount')] || '',
                currency: values[headers.indexOf('currency')] || '',
                description: values[headers.indexOf('description')] || '',
                account: values[headers.indexOf('account')] || '',
                category: values[headers.indexOf('category')] || '',
                payer: values[headers.indexOf('payer')] || '',
            };
        });
    };

    const validateData = (data: CSVRow[]): string[] => {
        const errors: string[] = [];
        
        data.forEach((row, index) => {
            const rowNumber = index + 2; // +2 because we skip header and arrays are 0-indexed
            
            if (!row.date) errors.push(`Row ${rowNumber}: Date is required`);
            if (!row.amount || isNaN(parseFloat(row.amount))) errors.push(`Row ${rowNumber}: Valid amount is required`);
            if (!row.currency) errors.push(`Row ${rowNumber}: Currency is required`);
            if (!row.account) errors.push(`Row ${rowNumber}: Account is required`);
            if (!row.category) errors.push(`Row ${rowNumber}: Category is required`);
            if (!row.payer) errors.push(`Row ${rowNumber}: Payer is required`);
            
            // Validate account exists
            const accountExists = accounts.some(acc => acc.name.toLowerCase() === row.account.toLowerCase());
            if (!accountExists) errors.push(`Row ${rowNumber}: Account "${row.account}" not found`);
            
            // Validate category exists
            const categoryExists = categories.some(cat => 
                cat.name.toLowerCase() === row.category.toLowerCase() && cat.type === 'expense'
            );
            if (!categoryExists) errors.push(`Row ${rowNumber}: Category "${row.category}" not found`);
            
            // Validate payer exists
            const payerExists = people.some(person => person.name.toLowerCase() === row.payer.toLowerCase());
            if (!payerExists) errors.push(`Row ${rowNumber}: Payer "${row.payer}" not found`);
        });
        
        return errors;
    };

    const convertToTransactions = (data: CSVRow[]): TransactionCreateExpense[] => {
        return data.map(row => {
            const account = accounts.find(acc => acc.name.toLowerCase() === row.account.toLowerCase());
            const category = categories.find(cat => 
                cat.name.toLowerCase() === row.category.toLowerCase() && cat.type === 'expense'
            );
            const payer = people.find(person => person.name.toLowerCase() === row.payer.toLowerCase());
            
            return {
                date: row.date,
                amount_total: parseFloat(row.amount),
                currency: row.currency,
                description: row.description,
                account_id: account!.id,
                category_id: category!.id,
                payer_person_id: payer!.id,
                type: 'expense' as const,
            };
        });
    };

    const handleCSVChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const csvText = e.target.value;
        setCsvData(csvText);
        
        if (csvText.trim()) {
            try {
                const parsed = parseCSV(csvText);
                setPreviewData(parsed.slice(0, 5)); // Show first 5 rows as preview
                setErrors([]);
            } catch (error) {
                setErrors([error instanceof Error ? error.message : 'Invalid CSV format']);
                setPreviewData([]);
            }
        } else {
            setPreviewData([]);
            setErrors([]);
        }
    };

    const handleImport = async () => {
        if (!csvData.trim()) return;
        
        try {
            setIsProcessing(true);
            const parsed = parseCSV(csvData);
            const validationErrors = validateData(parsed);
            
            if (validationErrors.length > 0) {
                setErrors(validationErrors);
                return;
            }
            
            const transactions = convertToTransactions(parsed);
            await onImport(transactions);
            
            // Reset form
            setCsvData('');
            setPreviewData([]);
            setErrors([]);
            setIsOpen(false);
            
            alert(`Successfully imported ${transactions.length} transactions!`);
        } catch (error) {
            setErrors([error instanceof Error ? error.message : 'Import failed']);
        } finally {
            setIsProcessing(false);
        }
    };

    const downloadTemplate = () => {
        const template = `date,amount,currency,description,account,category,payer
2024-01-15,25.50,USD,Grocery shopping,Main Account,Food,John Doe
2024-01-16,15.00,EUR,Coffee,Checking Account,Food,Jane Smith`;
        
        const blob = new Blob([template], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'expenses_template.csv';
        a.click();
        window.URL.revokeObjectURL(url);
    };

    return (
        <div className="mb-6">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="bg-gradient-to-r from-green-500 to-green-600 text-white px-6 py-3 rounded-lg hover:from-green-600 hover:to-green-700 transform hover:scale-105 transition-all duration-200 font-medium shadow-lg hover:shadow-xl flex items-center space-x-2"
            >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                </svg>
                <span>Import CSV</span>
            </button>

            {isOpen && (
                <div className="mt-4 p-6 bg-white border border-gray-200 rounded-lg shadow-lg">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-semibold text-gray-900">Import Expenses from CSV</h3>
                        <button
                            onClick={downloadTemplate}
                            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                        >
                            Download Template
                        </button>
                    </div>

                    <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            CSV Data (Paste your CSV content here)
                        </label>
                        <textarea
                            value={csvData}
                            onChange={handleCSVChange}
                            placeholder="Paste your CSV data here..."
                            className="w-full h-32 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                    </div>

                    {errors.length > 0 && (
                        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
                            <h4 className="text-sm font-medium text-red-800 mb-2">Validation Errors:</h4>
                            <ul className="text-sm text-red-700 space-y-1">
                                {errors.map((error, index) => (
                                    <li key={index}>• {error}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {previewData.length > 0 && (
                        <div className="mb-4">
                            <h4 className="text-sm font-medium text-gray-700 mb-2">Preview (first 5 rows):</h4>
                            <div className="overflow-x-auto">
                                <table className="min-w-full divide-y divide-gray-200">
                                    <thead className="bg-gray-50">
                                        <tr>
                                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Currency</th>
                                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Account</th>
                                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Payer</th>
                                        </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                        {previewData.map((row, index) => (
                                            <tr key={index}>
                                                <td className="px-3 py-2 text-sm text-gray-900">{row.date}</td>
                                                <td className="px-3 py-2 text-sm text-gray-900">{row.amount}</td>
                                                <td className="px-3 py-2 text-sm text-gray-900">{row.currency}</td>
                                                <td className="px-3 py-2 text-sm text-gray-900">{row.description}</td>
                                                <td className="px-3 py-2 text-sm text-gray-900">{row.account}</td>
                                                <td className="px-3 py-2 text-sm text-gray-900">{row.category}</td>
                                                <td className="px-3 py-2 text-sm text-gray-900">{row.payer}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    <div className="flex justify-end space-x-3">
                        <button
                            onClick={() => setIsOpen(false)}
                            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={handleImport}
                            disabled={isProcessing || errors.length > 0 || !csvData.trim()}
                            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isProcessing ? 'Importing...' : `Import ${previewData.length} Transactions`}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
