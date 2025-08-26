import React, { useEffect, useState } from 'react';
import { getAccounts, createAccount, updateAccount, deleteAccount } from '../api/accounts';
import { getCategories, createCategory, updateCategory, deleteCategory } from '../api/categories';
import { getPeople, createPerson, updatePerson, deletePerson } from '../api/people';
import Table, { Column } from '../components/Table';
import { Account, AccountCreate, Category, CategoryCreate, Person, PersonCreate } from '../types';

type TabType = 'accounts' | 'categories' | 'people';

export default function ManagementPage() {
    const [activeTab, setActiveTab] = useState<TabType>('accounts');
    
    // Accounts state
    const [accounts, setAccounts] = useState<Account[]>([]);
    const [accountForm, setAccountForm] = useState<AccountCreate>({
        name: "",
        currency: "",
        opening_balance: 0,
    });

    // Categories state
    const [categories, setCategories] = useState<Category[]>([]);
    const [categoryForm, setCategoryForm] = useState<CategoryCreate>({
        name: "",
        type: "expense",
    });

    // People state
    const [people, setPeople] = useState<Person[]>([]);
    const [personForm, setPersonForm] = useState<PersonCreate>({ 
        name: "", 
        is_me: false 
    });

    // Load data based on active tab
    useEffect(() => {
        switch (activeTab) {
            case 'accounts':
                getAccounts().then(setAccounts);
                break;
            case 'categories':
                getCategories().then(setCategories);
                break;
            case 'people':
                getPeople().then(setPeople);
                break;
        }
    }, [activeTab]);

    // Accounts handlers
    const handleAccountSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        await createAccount(accountForm);
        setAccountForm({ name: "", currency: "", opening_balance: 0 });
        getAccounts().then(setAccounts);
    };

    const handleAccountDelete = async (row: Account) => {
        if (window.confirm("Are you sure you want to delete this account?")) {
            await deleteAccount(row.id);
            getAccounts().then(setAccounts);
        }
    };

    const handleAccountSave = async (updatedAccount: Account) => {
        await updateAccount(updatedAccount.id, updatedAccount);
        getAccounts().then(setAccounts);
    };

    // Categories handlers
    const handleCategorySubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        await createCategory(categoryForm);
        setCategoryForm({ name: "", type: "expense" });
        getCategories().then(setCategories);
    };

    const handleCategoryDelete = async (row: Category) => {
        if (window.confirm("Are you sure you want to delete this category?")) {
            await deleteCategory(row.id);
            getCategories().then(setCategories);
        }
    };

    const handleCategorySave = async (updatedCategory: Category) => {
        await updateCategory(updatedCategory.id, updatedCategory);
        getCategories().then(setCategories);
    };

    // People handlers
    const handlePersonSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        await createPerson(personForm);
        setPersonForm({ name: "", is_me: false });
        getPeople().then(setPeople);
    };

    const handlePersonDelete = async (row: Person) => {
        if (window.confirm("Are you sure you want to delete this person?")) {
            await deletePerson(row.id);
            getPeople().then(setPeople);
        }
    };

    const handlePersonSave = async (updatedPerson: Person) => {
        await updatePerson(updatedPerson.id, updatedPerson);
        getPeople().then(setPeople);
    };

    // Column definitions
    const accountColumns: Column<Account>[] = [
        { label: "ID", accessor: "id" },
        { 
            label: "Name", 
            accessor: "name", 
            editable: true, 
            type: "text" 
        },
        { 
            label: "Currency", 
            accessor: "currency", 
            editable: true, 
            type: "select",
            options: [
                { value: "EUR", label: "EUR" },
                { value: "USD", label: "USD" },
                { value: "PEN", label: "PEN" }
            ]
        },
        { 
            label: "Opening Balance", 
            accessor: "opening_balance", 
            editable: true, 
            type: "number" 
        },
    ];

    const categoryColumns: Column<Category>[] = [
        { label: "ID", accessor: "id" },
        { 
            label: "Name", 
            accessor: "name",
            editable: true,
            type: "text"
        },
        { 
            label: "Type", 
            accessor: "type",
            editable: true,
            type: "select",
            options: [
                { value: "income", label: "Income" },
                { value: "expense", label: "Expense" }
            ]
        },
    ];

    const personColumns: Column<Person>[] = [
        { label: "ID", accessor: "id" },
        { 
            label: "Name", 
            accessor: "name",
            editable: true,
            type: "text"
        },
        { 
            label: "Is Me", 
            accessor: "is_me", 
            Cell: (val) => (val ? "Yes" : "No"),
            editable: true,
            type: "select",
            options: [
                { value: true, label: "Yes" },
                { value: false, label: "No" }
            ]
        },
    ];

    const renderTabContent = () => {
        switch (activeTab) {
            case 'accounts':
                return (
                    <div>
                        <form onSubmit={handleAccountSubmit} className="mb-4 space-x-2">
                            <input
                                type="text"
                                placeholder="Account Name"
                                className="border p-1"
                                value={accountForm.name}
                                onChange={(e) => setAccountForm({ ...accountForm, name: e.target.value })}
                            />
                            <select
                                className="border p-1"
                                value={accountForm.currency}
                                onChange={(e) => setAccountForm({ ...accountForm, currency: e.target.value })}
                            >
                                <option value="">Select Currency</option>
                                <option value="EUR">EUR</option>
                                <option value="USD">USD</option>
                                <option value="PEN">PEN</option>
                            </select>
                            <input
                                type="number"
                                step="0.01"
                                placeholder="Opening Balance"
                                className="border p-1"
                                value={accountForm.opening_balance}
                                onChange={(e) => setAccountForm({
                                    ...accountForm,
                                    opening_balance: parseFloat(e.target.value) || 0,
                                })}
                            />
                            <button type="submit" className="bg-green-600 text-white px-3 py-1 rounded">
                                Create Account
                            </button>
                        </form>
                        <Table<Account>
                            columns={accountColumns}
                            data={accounts}
                            onDelete={handleAccountDelete}
                            onSave={handleAccountSave}
                        />
                    </div>
                );

            case 'categories':
                return (
                    <div>
                        <form onSubmit={handleCategorySubmit} className="mb-4 space-x-2">
                            <input
                                type="text"
                                placeholder="Category Name"
                                className="border p-1"
                                value={categoryForm.name}
                                onChange={(e) => setCategoryForm({ ...categoryForm, name: e.target.value })}
                            />
                            <select 
                                className="border p-1"
                                value={categoryForm.type}
                                onChange={(e) => setCategoryForm({ ...categoryForm, type: e.target.value as CategoryCreate["type"] })}
                            >
                                <option value="income">Income</option>
                                <option value="expense">Expense</option>
                            </select>
                            <button type="submit" className="bg-blue-600 text-white px-3 py-1 rounded">
                                Create Category
                            </button>
                        </form>
                        <Table<Category>
                            columns={categoryColumns}
                            data={categories}
                            onDelete={handleCategoryDelete}
                            onSave={handleCategorySave}
                        />
                    </div>
                );

            case 'people':
                return (
                    <div>
                        <form onSubmit={handlePersonSubmit} className="mb-4 space-x-2">
                            <input
                                type="text"
                                placeholder="Person Name"
                                className="border p-1"
                                value={personForm.name}
                                onChange={(e) => setPersonForm({ ...personForm, name: e.target.value })}
                            />
                            <label className="inline-flex items-center">
                                <input
                                    type="checkbox"
                                    className="mr-1"
                                    checked={personForm.is_me}
                                    onChange={(e) => setPersonForm({ ...personForm, is_me: e.target.checked })}
                                />
                                It's me
                            </label>
                            <button type="submit" className="bg-blue-600 text-white px-3 py-1 rounded">
                                Create Person
                            </button>
                        </form>
                        <Table<Person>
                            columns={personColumns}
                            data={people}
                            onDelete={handlePersonDelete}
                            onSave={handlePersonSave}
                        />
                    </div>
                );

            default:
                return null;
        }
    };

    return (
        <div>
            <h1 className="text-xl font-bold mb-4">Management</h1>
            
            {/* Tab Navigation */}
            <div className="border-b border-gray-200 mb-6">
                <nav className="-mb-px flex space-x-8">
                    {[
                        { id: 'accounts' as TabType, label: 'Accounts' },
                        { id: 'categories' as TabType, label: 'Categories' },
                        { id: 'people' as TabType, label: 'People' }
                    ].map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`py-2 px-1 border-b-2 font-medium text-sm ${
                                activeTab === tab.id
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                        >
                            {tab.label}
                        </button>
                    ))}
                </nav>
            </div>

            {/* Tab Content */}
            {renderTabContent()}
        </div>
    );
}
