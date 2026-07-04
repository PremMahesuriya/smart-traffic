import axios from 'axios';

// Define the Express backend REST API base URL
const API_BASE_URL = 'http://localhost:5000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5000, // 5s timeout
});

export const apiService = {
  // 1. Health check
  healthCheck: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // 2. Traffic APIs
  getCurrentTraffic: async () => {
    const response = await apiClient.get('/traffic/current');
    return response.data;
  },

  getTrafficHistory: async () => {
    const response = await apiClient.get('/traffic/history');
    return response.data;
  },

  getTrafficAnalytics: async () => {
    const response = await apiClient.get('/traffic/analytics');
    return response.data;
  },

  // 3. Signal APIs
  getCurrentSignal: async () => {
    const response = await apiClient.get('/signals/current');
    return response.data;
  },

  getSignalHistory: async () => {
    const response = await apiClient.get('/signals/history');
    return response.data;
  },
};
export default apiService;
