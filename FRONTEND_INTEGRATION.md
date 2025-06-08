# Frontend Integration Configuration

## Prerequisites
- Node.js 16+ installed
- Package manager (npm, yarn, or pnpm)
- Backend server running on http://localhost:8000

## Quick Start Integration

### 1. Clone Frontend Repository
```bash
# Navigate to your project directory
cd ChamaWeb3

# Clone the frontend repository (replace with actual URL)
git clone <FRONTEND_REPOSITORY_URL> frontend

# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# or
yarn install
```

### 2. Environment Setup

Create `.env.local` (React) or `.env` file in the frontend directory:

```env
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:8000/api
REACT_APP_BACKEND_URL=http://localhost:8000

# Blockchain Configuration
REACT_APP_AVALANCHE_RPC_URL=https://api.avax-test.network/ext/bc/C/rpc
REACT_APP_AVALANCHE_CHAIN_ID=43113

# App Configuration
REACT_APP_APP_NAME=Chama Web3
REACT_APP_VERSION=1.0.0
```

### 3. Backend Server Start
```bash
# In the backend directory (ChamaWeb3/ChamaWeb3)
cd ../ChamaWeb3
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py runserver
```

### 4. Frontend Server Start
```bash
# In the frontend directory
cd ../frontend
npm start
# or
yarn start
```

## API Service Setup (React Example)

### api/config.js
```javascript
const API_CONFIG = {
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
};

export default API_CONFIG;
```

### api/client.js
```javascript
import axios from 'axios';
import API_CONFIG from './config';

class ApiClient {
  constructor() {
    this.client = axios.create(API_CONFIG);
    this.setupInterceptors();
  }

  setupInterceptors() {
    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
              const response = await this.client.post('/auth/token/refresh/', {
                refresh: refreshToken,
              });

              const { access } = response.data;
              localStorage.setItem('access_token', access);

              originalRequest.headers.Authorization = `Bearer ${access}`;
              return this.client(originalRequest);
            }
          } catch (refreshError) {
            // Refresh failed, redirect to login
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Auth methods
  async register(userData) {
    const response = await this.client.post('/users/register/', userData);
    return response.data;
  }

  async login(credentials) {
    const response = await this.client.post('/users/login/', credentials);
    const { access, refresh } = response.data;
    
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    
    return response.data;
  }

  async logout() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      await this.client.post('/users/logout/', { refresh: refreshToken });
    }
    
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  // User methods
  async getProfile() {
    const response = await this.client.get('/users/profile/');
    return response.data;
  }

  async updateProfile(profileData) {
    const response = await this.client.put('/users/profile/update/', profileData);
    return response.data;
  }

  // Chama methods
  async getGroups() {
    const response = await this.client.get('/chama/groups/');
    return response.data;
  }

  async createGroup(groupData) {
    const response = await this.client.post('/chama/groups/', groupData);
    return response.data;
  }

  async getGroup(groupId) {
    const response = await this.client.get(`/chama/groups/${groupId}/`);
    return response.data;
  }

  async joinGroup(groupId) {
    const response = await this.client.post(`/chama/groups/${groupId}/join/`);
    return response.data;
  }

  async leaveGroup(groupId) {
    const response = await this.client.post(`/chama/groups/${groupId}/leave/`);
    return response.data;
  }

  // Contribution methods
  async getContributions(params = {}) {
    const response = await this.client.get('/chama/contributions/', { params });
    return response.data;
  }

  async recordContribution(contributionData) {
    const response = await this.client.post('/chama/contributions/', contributionData);
    return response.data;
  }

  // Payout methods
  async getPayouts() {
    const response = await this.client.get('/chama/payouts/');
    return response.data;
  }

  async createPayout(payoutData) {
    const response = await this.client.post('/chama/payouts/', payoutData);
    return response.data;
  }

  // Dashboard
  async getDashboard() {
    const response = await this.client.get('/chama/dashboard/');
    return response.data;
  }

  // Transactions
  async getTransactions(params = {}) {
    const response = await this.client.get('/chama/transactions/', { params });
    return response.data;
  }
}

export default new ApiClient();
```

### hooks/useAuth.js (React Hook Example)
```javascript
import { useState, useEffect, createContext, useContext } from 'react';
import apiClient from '../api/client';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        const userData = await apiClient.getProfile();
        setUser(userData);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    try {
      const response = await apiClient.login(credentials);
      setUser(response.user);
      return response;
    } catch (error) {
      throw error;
    }
  };

  const register = async (userData) => {
    try {
      const response = await apiClient.register(userData);
      setUser(response.user);
      return response;
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await apiClient.logout();
    } finally {
      setUser(null);
    }
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
```

## Testing the Integration

### 1. Test Backend API
```bash
# Test user registration
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "phone_number": "1234567890",
    "password": "testpass123",
    "password_confirm": "testpass123"
  }'

# Test user login
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### 2. Test Frontend Connection
Create a simple test component to verify API connection:

```javascript
import { useState, useEffect } from 'react';
import apiClient from '../api/client';

const ApiTest = () => {
  const [status, setStatus] = useState('Testing...');

  useEffect(() => {
    testConnection();
  }, []);

  const testConnection = async () => {
    try {
      // Test if backend is reachable
      const response = await fetch('http://localhost:8000/api/');
      if (response.ok) {
        setStatus('✅ Backend connection successful!');
      } else {
        setStatus('❌ Backend connection failed');
      }
    } catch (error) {
      setStatus(`❌ Error: ${error.message}`);
    }
  };

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h2>API Connection Test</h2>
      <p>{status}</p>
    </div>
  );
};

export default ApiTest;
```

## Development Workflow

### 1. Start Both Servers
```bash
# Terminal 1: Backend
cd ChamaWeb3/ChamaWeb3
venv\Scripts\activate
python manage.py runserver

# Terminal 2: Frontend
cd ChamaWeb3/frontend
npm start
```

### 2. Access Points
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Django Admin: http://localhost:8000/admin/

### 3. Development Tools
- Browser DevTools for frontend debugging
- Django Debug Toolbar for backend debugging
- Postman/Insomnia for API testing

## Common Issues & Solutions

### CORS Issues
If you get CORS errors, ensure the frontend URL is added to `CORS_ALLOWED_ORIGINS` in Django settings.

### Authentication Issues
- Check token storage in localStorage
- Verify token format (Bearer token)
- Check token expiration

### API URL Issues
- Ensure API base URL is correct
- Check for trailing slashes
- Verify environment variables

## Next Steps
1. Clone and set up the frontend repository
2. Configure environment variables
3. Test API integration
4. Implement authentication flow
5. Build Chama group management UI
6. Add Web3 wallet integration
7. Implement contribution and payout features
