import api from './axiosInstance';

export const getBudget = async (id, month) => {
    const response = await api.get(`/budgets/${id}/${month}`);
    return response.data;
};

export const getAnnualBudget = async (id) => {
    const response = await api.get(`/budgets/${id}`);
    return response.data;
};

export const createBudget = async (budget) => {
    const response = await api.post('/budgets', budget);
    return response.data;
};

export const updateBudget = async (id, budget) => {
    const response = await api.patch(`/budgets/${id}`, budget);
    return response.data;
};

export const deleteBudget = async (id) => {
    await api.delete(`/budgets/${id}`);
};
