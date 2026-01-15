import axios from 'axios';
import authService from './authService';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://api.example.com/prod';

class ServiceAPI {
  async getServices() {
    try {
      const response = await axios.get(`${API_BASE_URL}/services`, {
        headers: authService.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async requestService(category, requestData) {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/services/request`,
        { category, requestData },
        { headers: authService.getAuthHeaders() }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async processWithAgent(agentType, requestData) {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/agents/process`,
        { agentType, requestData },
        { headers: authService.getAuthHeaders() }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getSubscription() {
    try {
      const response = await axios.get(`${API_BASE_URL}/subscription`, {
        headers: authService.getAuthHeaders()
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async updateSubscription(membershipTier) {
    try {
      const response = await axios.put(
        `${API_BASE_URL}/subscription`,
        { membershipTier },
        { headers: authService.getAuthHeaders() }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  handleError(error) {
    if (error.response) {
      return new Error(error.response.data.error || 'An error occurred');
    } else if (error.request) {
      return new Error('No response from server');
    } else {
      return new Error('Request failed');
    }
  }
}

export default new ServiceAPI();
