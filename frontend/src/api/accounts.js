import api from './axiosInstance';

export const getAccounts = async () => {
    const response = await api.get('/accounts');
    return response.data;
};

export const getAccount = async (id) => {
    const response = await api.get(`/accounts/${id}`);
    return response.data;
};

export const createAccount = async (account) => {
    const response = await api.post('/accounts', account);
    return response.data;
};

export const updateAccount = async (id, account) => {
    const response = await api.patch(`/accounts/${id}`, account);
    return response.data;
};

export const deleteAccount = async (id) => {
    await api.delete(`/accounts/${id}`);
};