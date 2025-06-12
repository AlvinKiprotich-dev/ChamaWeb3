# Chama Web3 Platform

A full-stack Chama (rotating savings group) platform with Django backend and React frontend, featuring email verification, JWT authentication, and Web3 integration capabilities.

## 🏗️ Architecture

- **Backend**: Django REST Framework with JWT authentication
- **Frontend**: React + TypeScript + Vite + TailwindCSS
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: JWT tokens with email verification
- **API**: RESTful API with React Query integration

## ✨ Features

### Backend Features
- **User Management**: Registration with email verification, JWT authentication
- **Chama Groups**: Create and manage rotating savings groups
- **Contributions**: Track member contributions and payments
- **Email System**: Email verification and notifications
- **Background Tasks**: Celery-powered payout scheduling
- **Web3 Ready**: Avalanche blockchain integration framework

### Frontend Features
- **Modern React**: TypeScript, Vite, TailwindCSS, shadcn/ui
- **Authentication Flow**: Login, register, email verification, password reset
- **Protected Routes**: JWT-based route protection
- **API Integration**: React Query for efficient data fetching
- **Responsive Design**: Mobile-first responsive UI
- **Real-time Updates**: Optimistic updates and error handling

## 🚀 Quick Start

### Backend Setup

1. **Navigate to project directory:**
   ```bash
   cd ChamaWeb3
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up database:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Start Django server:**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

### Access the Application

- **Frontend**: http://localhost:8081/
- **Backend API**: http://127.0.0.1:8000/api/
- **Django Admin**: http://127.0.0.1:8000/admin/

## ⚙️ Configuration

### Backend Environment Variables
Create a `.env` file in the root directory:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here

# Email Configuration (for development - prints to console)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Frontend URL (for email verification links)
FRONTEND_URL=http://localhost:8081

# Database (SQLite for development)
# DB_NAME=chama_db
# DB_USER=chama_user  
# DB_PASSWORD=chama_password
# DB_HOST=localhost
# DB_PORT=5432

# Avalanche Configuration (for future Web3 features)
AVALANCHE_RPC_URL=https://api.avax-test.network/ext/bc/C/rpc
   AVALANCHE_CHAIN_ID=43113
   CHAMA_CONTRACT_ADDRESS=your-contract-address
   ADMIN_PRIVATE_KEY=your-wallet-private-key
   
   # Redis (for production)
   REDIS_URL=redis://localhost:6379/0
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server:**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### User Management
- `POST /api/users/register/` - User registration
- `POST /api/users/login/` - User login
- `POST /api/users/logout/` - User logout
- `GET /api/users/profile/` - Get user profile
- `PUT /api/users/profile/update/` - Update user profile
- `POST /api/users/change-password/` - Change password

### Chama Groups
- `GET /api/chama/groups/` - List all groups
- `POST /api/chama/groups/` - Create new group
- `GET /api/chama/groups/{id}/` - Get group details
- `PUT /api/chama/groups/{id}/` - Update group
- `DELETE /api/chama/groups/{id}/` - Delete group
- `POST /api/chama/groups/{id}/join/` - Join group
- `POST /api/chama/groups/{id}/leave/` - Leave group

### Contributions
- `GET /api/chama/contributions/` - List contributions
- `POST /api/chama/contributions/` - Record contribution
- `GET /api/chama/contributions/{id}/` - Get contribution details

### Payouts
- `GET /api/chama/payouts/` - List payouts
- `POST /api/chama/payouts/` - Create payout
- `GET /api/chama/payouts/{id}/` - Get payout details

### Transactions
- `GET /api/chama/transactions/` - List blockchain transactions
- `GET /api/chama/transactions/{id}/` - Get transaction details

### Dashboard
- `GET /api/chama/dashboard/` - Get user dashboard data

## Database Models

### User Model
- Custom user model with email, phone, wallet address
- Profile picture and verification status

### ChamaGroup Model
- Group management with contribution amounts and schedules
- Support for merry-go-round type groups
- Member limits and group status

### GroupMembership Model
- Track member participation and order in groups
- Join/leave dates and member status

### Contribution Model
- Record member contributions with amounts and dates
- Blockchain transaction linking

### Payout Model
- Schedule and track payouts to members
- Integration with blockchain transactions

### Transaction Model
- Blockchain transaction records
- Gas fees and confirmation status

## Celery Tasks

Background tasks for:
- Blockchain transaction verification
- Scheduled payouts
- Email/SMS notifications
- Data cleanup and maintenance

### Running Celery Worker

```bash
# In a separate terminal
celery -A chama_backend worker --loglevel=info
```

### Running Celery Beat (for scheduled tasks)

```bash
# In another terminal
celery -A chama_backend beat --loglevel=info
```

## Development vs Production

### Development (Current Setup)
- SQLite database
- Django database for Celery broker
- Debug mode enabled
- Local file logging

### Production Setup
- PostgreSQL database
- Redis for Celery broker
- Debug mode disabled
- Production logging configuration

## Admin Interface

Access the Django admin at: `http://127.0.0.1:8000/admin/`

Manage:
- Users and groups
- Chama groups and memberships
- Contributions and payouts
- Blockchain transactions
- Celery periodic tasks

## Testing the API

You can test the API endpoints using:
- Django REST Framework browsable API: `http://127.0.0.1:8000/api/`
- Postman or similar API testing tools
- Frontend integration

### Frontend Environment Variables
Create a `.env` file in the `frontend/` directory:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
VITE_APP_NAME=ChamaWeb3
VITE_APP_VERSION=1.0.0
```

## 🧪 Testing the Application

### 1. User Registration Flow
1. Navigate to http://localhost:8081/
2. Click "Register" and fill out the form
3. Check Django console for verification email output
4. Copy verification link and paste in browser
5. Verify email and login

### 2. Authentication Flow
- **Before verification**: Login should be blocked
- **After verification**: Login should work and redirect to dashboard
- **Protected routes**: Dashboard requires authentication

### 3. API Testing
The backend provides these main endpoints:
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `GET /api/auth/verify-email/` - Email verification
- `POST /api/auth/resend-verification/` - Resend verification email
- `GET /api/auth/profile/` - User profile (authenticated)

## 📁 Project Structure

```
ChamaWeb3/
├── chama_backend/          # Django settings
├── users/                  # User authentication app
├── chama/                  # Chama groups app
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # React Query hooks
│   │   ├── lib/            # API and utilities
│   │   └── contexts/       # React contexts
├── static/                 # Static files
├── logs/                   # Application logs
└── requirements.txt        # Python dependencies
```
