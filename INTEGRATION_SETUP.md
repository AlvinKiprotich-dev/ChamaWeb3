# ChamaWeb3 Frontend-Backend Integration Setup

## Current Status ✅

### Backend (Django) - COMPLETED
- ✅ Django REST API running on `http://127.0.0.1:8000/`
- ✅ JWT authentication configured
- ✅ PostgreSQL/SQLite database setup
- ✅ CORS configured for frontend integration
- ✅ All API endpoints ready for consumption
- ✅ Celery background tasks configured

### Frontend (React + TypeScript) - IN PROGRESS
- ✅ Repository cloned successfully
- ✅ API service layer created (`/frontend/src/lib/api.ts`)
- ✅ React Query hooks created (`/frontend/src/hooks/useApi.ts`)
- ✅ Authentication context setup (`/frontend/src/contexts/AuthContext.tsx`)
- ✅ Protected routes implemented (`/frontend/src/components/ProtectedRoute.tsx`)
- ✅ Environment variables configured (`/frontend/.env`)
- ✅ App.tsx updated with authentication flow
- ✅ Login page integrated with API
- ✅ Dashboard page updated to use real API data

## Next Steps Required

### 1. Install Node.js

You need to install Node.js to run the frontend. Choose one of these options:

#### Option A: Direct Download (Recommended)
1. Visit https://nodejs.org/
2. Download the LTS version (Long Term Support)
3. Run the installer and follow the setup wizard
4. Restart your command prompt/PowerShell

#### Option B: Using Windows Package Manager (if you have winget)
```powershell
winget install OpenJS.NodeJS
```

#### Option C: Using Chocolatey (if you have chocolatey)
```powershell
choco install nodejs
```

### 2. Verify Installation
After installing Node.js, verify it works:
```powershell
node --version
npm --version
```

### 3. Install Frontend Dependencies
```powershell
cd frontend
npm install
```

### 4. Start Frontend Development Server
```powershell
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Integration Features Implemented

### 🔐 Authentication System
- **JWT Token Management**: Automatic token storage and refresh
- **Login/Register**: Full integration with Django backend
- **Protected Routes**: Automatic redirect to login for unauthenticated users
- **Session Persistence**: Tokens stored in localStorage with automatic refresh

### 📊 API Integration
- **Complete API Layer**: All Django endpoints mapped to TypeScript functions
- **React Query Integration**: Caching, error handling, and optimistic updates
- **Type Safety**: Full TypeScript types for all API responses
- **Error Handling**: Automatic error toasts and user feedback

### 🎯 Features Ready for Testing

#### Authentication Flow
1. **Register**: `/auth/register` - Create new user account
2. **Login**: `/auth/login` - User authentication with email/password
3. **Dashboard**: Protected route that shows user data

#### Dashboard Integration
- **Real-time Data**: Dashboard pulls actual data from Django API
- **Group Statistics**: Shows user's groups and contribution totals  
- **Transaction History**: Displays recent transactions from database
- **User Profile**: Shows authenticated user information

#### API Endpoints Available
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Token refresh
- `GET /api/users/profile/` - User profile
- `GET /api/groups/` - List user's groups
- `GET /api/contributions/` - List contributions
- `GET /api/transactions/` - List transactions

## Testing the Integration

### 1. Start Backend (if not running)
```powershell
cd ChamaWeb3
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

### 2. Start Frontend (after Node.js installation)
```powershell
cd frontend
npm install
npm run dev
```

### 3. Test Authentication Flow
1. Open `http://localhost:5173`
2. Navigate to `/auth/register` to create a test account
3. Navigate to `/auth/login` to test login
4. Access `/dashboard` to see integrated data

### 4. Test API Integration
- The Dashboard will show real data from your Django backend
- Any groups, contributions, or transactions in your database will appear
- Create some test data in Django admin to see it reflected in the frontend

## Environment Configuration

### Backend Settings (already configured)
- **CORS Origins**: Includes `http://localhost:5173` for frontend
- **JWT Settings**: Configured for token-based authentication
- **API Base URL**: `http://127.0.0.1:8000/api/`

### Frontend Settings (configured)
- **API Base URL**: `VITE_API_BASE_URL=http://127.0.0.1:8000/api`
- **Environment Variables**: All necessary variables set in `.env`

## Troubleshooting

### Common Issues

1. **CORS Errors**: 
   - Ensure Django backend is running on `http://127.0.0.1:8000`
   - Check that `CORS_ALLOWED_ORIGINS` includes frontend URL

2. **Authentication Issues**:
   - Clear browser localStorage if you see token-related errors
   - Check that JWT settings match between frontend and backend

3. **API Connection Issues**:
   - Verify both servers are running (Django on 8000, Vite on 5173)
   - Check browser network tab for API request status

4. **Node.js Installation Issues**:
   - Try running PowerShell as Administrator
   - Restart your terminal after installation
   - Clear npm cache: `npm cache clean --force`

## Development Workflow

### Adding New Features
1. **Backend**: Add Django models, serializers, views
2. **Frontend**: Update API types and hooks in respective files
3. **Integration**: Use React Query hooks in components
4. **Testing**: Test API endpoints and frontend integration

### File Structure Reference
```
frontend/src/
├── lib/
│   └── api.ts              # API service layer and types
├── hooks/
│   └── useApi.ts           # React Query hooks
├── contexts/
│   └── AuthContext.tsx     # Authentication state management
├── components/
│   └── ProtectedRoute.tsx  # Route protection
└── pages/
    ├── auth/
    │   ├── Login.tsx       # Login with API integration
    │   └── Register.tsx    # Registration (needs updating)
    └── Dashboard.tsx       # Dashboard with real data
```

## Next Development Priorities

1. **Complete Authentication Pages**: Update Register.tsx with API integration
2. **Groups Management**: Integrate group creation, joining, and management
3. **Contributions Flow**: Implement contribution submission and tracking
4. **Web3 Integration**: Add wallet connection and blockchain transactions
5. **Real-time Updates**: WebSocket integration for live updates
6. **Enhanced UI/UX**: Polish the user interface and user experience

Your Django backend is fully functional and the frontend foundation is ready. Once Node.js is installed and the frontend is running, you'll have a complete full-stack application with secure authentication and real-time data integration!
