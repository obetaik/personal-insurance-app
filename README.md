# Personal Insurance Application

A full-stack insurance management application with authentication, quotes, policies, claims, and user profiles.

## 🚀 Features

- **User Authentication** with Auth0
- **Product Catalog** - Browse insurance products
- **Quotes** - Get instant quotes for insurance products
- **Policies** - Manage active policies
- **Claims** - File and track claims
- **Payments** - Process payments
- **User Profile** - Manage personal information
- **Dashboard** - Overview of user's insurance status

## 🛠️ Tech Stack

### Backend
- Python Flask
- MySQL Database
- SQLAlchemy ORM
- Auth0 for authentication
- Gunicorn WSGI server
- Docker containerization

### Frontend
- React 19
- Vite build tool
- React Bootstrap for UI
- Auth0 React SDK
- Axios for API calls
- React Router for navigation

### Testing
- Vitest for unit tests
- React Testing Library
- Coverage reports with v8

## 📋 Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)
- Auth0 account (for authentication)

## 🚦 Getting Started

### Using Docker (Recommended)

1. Clone the repository
2. Create .env files in both ackend/ and rontend/ directories (see .env.example)
3. Run with Docker Compose:
   \\\ash
   docker-compose up -d
   \\\
4. Access the application:
   - Frontend: http://localhost
   - Backend API: http://localhost:4000

### Local Development

#### Backend
\\\ash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
\\\

#### Frontend
\\\ash
cd frontend
npm install
npm run dev
\\\

## 🧪 Running Tests

### Backend Tests
\\\ash
cd backend
pytest
\\\

### Frontend Tests
\\\ash
cd frontend
npm test
npm run test:coverage  # With coverage
\\\

## 📁 Project Structure

\\\
personal-insurance-app/
├── backend/                 # Flask backend
│   ├── app.py              # Main application
│   ├── models.py           # Database models
│   ├── auth.py             # Auth0 authentication
│   ├── config.py           # Configuration
│   └── requirements.txt    # Python dependencies
├── frontend/                # React frontend
│   ├── src/
│   │   ├── pages/          # Page components
│   │   ├── context/        # React context
│   │   ├── services/       # API services
│   │   └── __tests__/      # Test files
│   └── package.json        # Node dependencies
├── database/                # SQL scripts
│   ├── schema.sql          # Database schema
│   └── sample-data.sql     # Sample data
├── docker-compose.yml       # Docker composition
└── .gitignore              # Git ignore file
\\\

## 🔐 Environment Variables

### Backend (.env)
\\\
DATABASE_URL=mysql+pymysql://user:password@mysql:3306/insurance_db
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_API_AUDIENCE=https://your-api
AUTH0_ALGORITHMS=RS256
\\\

### Frontend (.env)
\\\
VITE_API_URL=http://localhost:4000/api
VITE_AUTH0_DOMAIN=your-domain.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id
VITE_AUTH0_CALLBACK_URL=http://localhost:5173
VITE_AUTH0_AUDIENCE=https://your-api
\\\

## 📦 Docker Commands

\\\ash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild specific service
docker-compose build backend
docker-compose build frontend

# Reset everything (including database)
docker-compose down -v
docker-compose up -d
\\\

## 👥 Contributing

1. Fork the repository
2. Create your feature branch (\git checkout -b feature/AmazingFeature\)
3. Commit your changes (\git commit -m 'Add some AmazingFeature'\)
4. Push to the branch (\git push origin feature/AmazingFeature\)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Auth0 for authentication
- React Bootstrap for UI components
- Flask and SQLAlchemy community
