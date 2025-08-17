import axios from 'axios';
// Axios instance configured with the backend URL
const api = axios.create({
baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
});
export default api;