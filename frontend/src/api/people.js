import api from './axiosInstance';

export const createPerson = async (person) => {
    const response = await api  .post('/people', person);
    return response.data;
};

export const getPeople = async () => {
    const response = await api.get('/people');
    return response.data;
};

export const getPerson = async (id) => {
    const response = await api.get(`/people/${id}`);
    return response.data;
};

export const updatePerson = async (id, person) => {
    const response = await api.put(`/people/${id}`, person);
    return response.data;
};

export const deletePerson = async (id) => {
    await api.delete(`/people/${id}`);
};