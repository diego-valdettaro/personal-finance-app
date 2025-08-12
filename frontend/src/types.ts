export type Account = { id: number; name: string; currency: string};
export type Category = { id: number; name: string; type: 'income' | 'expense'};
export type Transaction = {
    id: number;
    date: string;
    amount: number;
    currency: string;
    type: 'income' | 'expense';
    description?: string;
    detail_json?: string;
    account_id: number;
    category_id: number;
};
