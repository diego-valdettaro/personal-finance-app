import api from './axiosInstance';

export const getBalances = async () => {
    const response = await api.get('/reports/balances');
    return response.data;
};

export const getDebts = async () => {
    const response = await api.get('/reports/debts');
    return response.data;
};

export const getBudgetProgress = async (month) => {
    const response = await api.get(`/reports/budget-progress/${month}`);
    return response.data;
};