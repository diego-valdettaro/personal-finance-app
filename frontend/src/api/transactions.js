import api from './axiosInstance';

export const getTransactions = async (filters) => {
    const response = await api.get('/transactions', { params: filters });
    return response.data;
};

export const getTransaction = async (id) => {
    const response = await api.get(`/transactions/${id}`);
    return response.data;
};

export const createTransaction = async (transaction) => {
    const response = await api.post('/transactions', transaction);
    return response.data;
};

export const updateTransaction = async (id, transaction) => {
    const response = await api.patch(`/transactions/${id}`, transaction);
    return response.data;
};

export const deleteTransaction = async (id) => {
    await api.delete(`/transactions/${id}`);
};

// Pending validation: shares is an array of objects with person_id and amount
export const splitTransaction = async (id, payerPersonId, shares) => {
    const response = await api.post(`/transactions/${id}/split`, { payer_person_id: payerPersonId, shares });
    return response.data;
};