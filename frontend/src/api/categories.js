import api from './axiosInstance';

export const getCategories = async () => {
    const response = await api.get('/categories');
    return response.data;
};

export const getCategory = async (id) => {
    const response = await api.get(`/categories/${id}`);
    return response.data;
};

export const createCategory = async (category) => {
    const response = await api.post('/categories', category);
    return response.data;
};

export const updateCategory = async (id, category) => {
    const response = await api.patch(`/categories/${id}`, category);
    return response.data;
};

export const deleteCategory = async (id) => {
    await api.delete(`/categories/${id}`);
};