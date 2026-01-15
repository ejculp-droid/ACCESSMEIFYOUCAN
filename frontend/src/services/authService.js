import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://api.example.com/prod';

class AuthService {
  constructor() {
    this.token = localStorage.getItem('accessToken');
    this.user = JSON.parse(localStorage.getItem('user') || 'null');
  }

  async register(email, password) {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/register`, {
        email,
        password
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async login(email, password) {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        email,
        password
      });
      
      const { accessToken, idToken, refreshToken, membershipTier } = response.data;
      
      // Store tokens
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('idToken', idToken);
      localStorage.setItem('refreshToken', refreshToken);
      
      // Store user info
      const user = { email, membershipTier };
      localStorage.setItem('user', JSON.stringify(user));
      
      this.token = accessToken;
      this.user = user;
      
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  logout() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('idToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    this.token = null;
    this.user = null;
  }

  isAuthenticated() {
    return !!this.token;
  }

  getToken() {
    return this.token;
  }

  getUser() {
    return this.user;
  }

  getAuthHeaders() {
    return {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json'
    };
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

export default new AuthService();
