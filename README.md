# Chama Web3 Backend

A Django backend for a Chama (rotating savings group) platform that bridges frontend applications with Avalanche blockchain smart contracts.

## Features

- **User Management**: Registration, authentication, profile management
- **Chama Groups**: Create and manage rotating savings groups (merry-go-round type)
- **Contributions**: Track member contributions to groups
- **Blockchain Integration**: Web3 integration with Avalanche network
- **Background Tasks**: Celery-powered payout scheduling and notifications
- **RESTful API**: Django REST Framework powered API endpoints

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL (for production) or SQLite (for development)
- Redis (for production Celery) or Django database (for development)

### Installation

1. **Clone and navigate to the project:**
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

4. **Environment Variables:**
   Create a `.env` file in the project root:
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   
   # Database (for production)
   DB_NAME=chama_db
   DB_USER=chama_user
   DB_PASSWORD=chama_password
   DB_HOST=localhost
   DB_PORT=5432
   
   # Avalanche Configuration
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

## Next Steps

1. **Deploy Smart Contract**: Deploy your Chama smart contract to Avalanche
2. **Frontend Integration**: Connect with React/Vue frontend
3. **Production Deployment**: Set up PostgreSQL and Redis
4. **Testing**: Add comprehensive test suite
5. **Documentation**: API documentation with tools like Swagger/OpenAPI

## Support

For issues and questions, refer to the Django and DRF documentation, or check the project logs in the `logs/` directory.
