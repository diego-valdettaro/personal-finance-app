export type Person = {
    id: number;
    name: string;
    is_me: boolean;
};

export type PersonCreate = {
    name: string;
    is_me: boolean;
}

export type Account = { 
    id: number; 
    name: string; 
    currency: string;
    opening_balance: number;
};

export type AccountCreate = {
    name: string;
    currency: string;
    opening_balance: number;
};

export type Category = {
    id: number;
    name: string;
    type: "income" | "expense";
};

export type CategoryCreate = {
    name: string;
    type: "income" | "expense";
};

export type Transaction = {
    id: number;
    date: string;
    amount_total: number;
    currency: string;
    type: "income" | "expense";
    description?: string;
    account_id: number;
    category_id: number;
    payer_person_id: number;
};


export type ExpenseForm = {
    date: string;
    amount_total: number;
    currency: string;
    description: string;
    account_id: number | "";
    category_id: number | "";
    payer_person_id: number | "";
};

export type TransactionCreateExpense = {
    date: string;
    amount_total: number;
    currency: string;
    description: string;
    account_id: number;
    category_id: number;
    payer_person_id: number;
    type: "expense";	
};

export type BalanceRow = {
    id?: number | string;
    account_name?: string;
    balance: number;
}

export type Debt = {
    id: number;
    person_name: string;
    debt: number;
    is_active: boolean;
};

export type TransactionFilters = Partial<{
    date_from: string;
    date_to: string;
    account_id: number;
    category_id: number;
    payer_person_id: number;
}>;

export type SplitPayload = {
    payer_person_id: number;
    shares: {
        person_id: number;
        amount: number;
        source: "user_manual";
    }[];
};