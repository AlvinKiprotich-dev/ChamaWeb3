# Chama Web3 Backend API Documentation

## Base URL
- **Development**: `http://localhost:8000/api/`
- **Production**: `https://your-domain.com/api/`

## Authentication
All authenticated endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Content Type
All requests should use:
```
Content-Type: application/json
```

---

## 🔐 Authentication Endpoints

### 1. User Registration
**POST** `/users/register/`

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "phone_number": "1234567890",
  "password": "securepassword",
  "password_confirm": "securepassword"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "phone_number": "1234567890",
    "is_verified": false
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 2. User Login
**POST** `/users/login/`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username"
  }
}
```

### 3. User Logout
**POST** `/users/logout/`
*Requires Authentication*

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

### 4. Get User Profile
**GET** `/users/profile/`
*Requires Authentication*

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "phone_number": "1234567890",
  "wallet_address": "0x1234...",
  "profile_picture": null,
  "is_verified": false,
  "date_joined": "2025-06-05T10:00:00Z"
}
```

### 5. Update User Profile
**PUT** `/users/profile/update/`
*Requires Authentication*

**Request Body:**
```json
{
  "username": "newusername",
  "phone_number": "0987654321",
  "wallet_address": "0x5678..."
}
```

### 6. Change Password
**POST** `/users/change-password/`
*Requires Authentication*

**Request Body:**
```json
{
  "old_password": "oldpassword",
  "new_password": "newpassword",
  "new_password_confirm": "newpassword"
}
```

---

## 👥 Chama Group Endpoints

### 1. List Groups
**GET** `/chama/groups/`
*Requires Authentication*

**Response (200 OK):**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Savings Group 1",
      "description": "Monthly savings group",
      "creator": {
        "id": 1,
        "username": "creator"
      },
      "contribution_amount": "1000.00",
      "contribution_frequency": "monthly",
      "max_members": 10,
      "current_members": 5,
      "group_type": "merry_go_round",
      "status": "active",
      "created_at": "2025-06-01T10:00:00Z"
    }
  ]
}
```

### 2. Create Group
**POST** `/chama/groups/`
*Requires Authentication*

**Request Body:**
```json
{
  "name": "My Chama Group",
  "description": "Weekly savings group",
  "contribution_amount": "500.00",
  "contribution_frequency": "weekly",
  "max_members": 8,
  "group_type": "merry_go_round"
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "name": "My Chama Group",
  "description": "Weekly savings group",
  "creator": {
    "id": 1,
    "username": "creator"
  },
  "contribution_amount": "500.00",
  "contribution_frequency": "weekly",
  "max_members": 8,
  "current_members": 1,
  "group_type": "merry_go_round",
  "status": "active",
  "created_at": "2025-06-05T10:00:00Z"
}
```

### 3. Get Group Details
**GET** `/chama/groups/{id}/`
*Requires Authentication*

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Savings Group 1",
  "description": "Monthly savings group",
  "creator": {
    "id": 1,
    "username": "creator",
    "email": "creator@example.com"
  },
  "members": [
    {
      "id": 1,
      "member": {
        "id": 1,
        "username": "member1"
      },
      "order": 1,
      "joined_at": "2025-06-01T10:00:00Z",
      "status": "active"
    }
  ],
  "contribution_amount": "1000.00",
  "contribution_frequency": "monthly",
  "max_members": 10,
  "current_members": 5,
  "group_type": "merry_go_round",
  "status": "active",
  "next_payout_date": "2025-07-01T10:00:00Z",
  "total_contributions": "5000.00",
  "created_at": "2025-06-01T10:00:00Z"
}
```

### 4. Join Group
**POST** `/chama/groups/{id}/join/`
*Requires Authentication*

**Response (200 OK):**
```json
{
  "message": "Successfully joined the group",
  "membership": {
    "id": 6,
    "order": 6,
    "joined_at": "2025-06-05T10:00:00Z",
    "status": "active"
  }
}
```

### 5. Leave Group
**POST** `/chama/groups/{id}/leave/`
*Requires Authentication*

**Response (200 OK):**
```json
{
  "message": "Successfully left the group"
}
```

---

## 💰 Contribution Endpoints

### 1. List Contributions
**GET** `/chama/contributions/`
*Requires Authentication*

**Query Parameters:**
- `group_id` (optional): Filter by group
- `date_from` (optional): Filter from date (YYYY-MM-DD)
- `date_to` (optional): Filter to date (YYYY-MM-DD)

**Response (200 OK):**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "group": {
        "id": 1,
        "name": "Savings Group 1"
      },
      "contributor": {
        "id": 1,
        "username": "member1"
      },
      "amount": "1000.00",
      "contribution_date": "2025-06-01T10:00:00Z",
      "blockchain_transaction": {
        "id": 1,
        "transaction_hash": "0xabc123...",
        "status": "confirmed"
      },
      "status": "confirmed"
    }
  ]
}
```

### 2. Record Contribution
**POST** `/chama/contributions/`
*Requires Authentication*

**Request Body:**
```json
{
  "group_id": 1,
  "amount": "1000.00",
  "transaction_hash": "0xabc123..."
}
```

**Response (201 Created):**
```json
{
  "id": 11,
  "group": {
    "id": 1,
    "name": "Savings Group 1"
  },
  "contributor": {
    "id": 1,
    "username": "member1"
  },
  "amount": "1000.00",
  "contribution_date": "2025-06-05T10:00:00Z",
  "blockchain_transaction": {
    "id": 2,
    "transaction_hash": "0xabc123...",
    "status": "pending"
  },
  "status": "pending"
}
```

---

## 🎯 Payout Endpoints

### 1. List Payouts
**GET** `/chama/payouts/`
*Requires Authentication*

**Response (200 OK):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "group": {
        "id": 1,
        "name": "Savings Group 1"
      },
      "recipient": {
        "id": 2,
        "username": "member2"
      },
      "amount": "5000.00",
      "scheduled_date": "2025-07-01T10:00:00Z",
      "actual_payout_date": null,
      "status": "scheduled",
      "blockchain_transaction": null
    }
  ]
}
```

### 2. Create Payout
**POST** `/chama/payouts/`
*Requires Authentication*

**Request Body:**
```json
{
  "group_id": 1,
  "recipient_id": 2,
  "amount": "5000.00",
  "scheduled_date": "2025-07-01T10:00:00Z"
}
```

---

## 📊 Dashboard Endpoint

### Get User Dashboard
**GET** `/chama/dashboard/`
*Requires Authentication*

**Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "username": "user1",
    "email": "user@example.com"
  },
  "groups_count": 3,
  "total_contributions": "15000.00",
  "total_payouts_received": "5000.00",
  "pending_contributions": "2000.00",
  "upcoming_payouts": [
    {
      "id": 1,
      "group_name": "Savings Group 1",
      "amount": "5000.00",
      "scheduled_date": "2025-07-01T10:00:00Z"
    }
  ],
  "recent_activities": [
    {
      "type": "contribution",
      "description": "Contributed KES 1000 to Savings Group 1",
      "date": "2025-06-05T10:00:00Z"
    }
  ]
}
```

---

## 📦 Transaction Endpoints

### 1. List Transactions
**GET** `/chama/transactions/`
*Requires Authentication*

**Response (200 OK):**
```json
{
  "count": 20,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "transaction_hash": "0xabc123...",
      "transaction_type": "contribution",
      "amount": "1000.00",
      "gas_fee": "0.001",
      "status": "confirmed",
      "block_number": 12345,
      "created_at": "2025-06-05T10:00:00Z",
      "confirmed_at": "2025-06-05T10:02:00Z"
    }
  ]
}
```

---

## 🚨 Error Responses

### 400 Bad Request
```json
{
  "error": "Validation failed",
  "details": {
    "email": ["This field is required."],
    "password": ["This field is required."]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred."
}
```

---

## 🔧 Frontend Integration Notes

### 1. Environment Variables
Create a `.env` file in your frontend project:
```env
REACT_APP_API_BASE_URL=http://localhost:8000/api
REACT_APP_WEBSOCKET_URL=ws://localhost:8000/ws
```

### 2. Axios Configuration Example
```javascript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
```

### 3. CORS Settings
The backend is already configured to accept requests from:
- `http://localhost:3000` (React dev server)
- `http://localhost:8080` (Vue dev server)
- `http://127.0.0.1:3000`
- `http://127.0.0.1:8080`

### 4. WebSocket Support (Future)
WebSocket endpoints will be available for real-time features:
- Group notifications
- Transaction updates
- Payout alerts
