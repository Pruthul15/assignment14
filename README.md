# Assignment 14: BREAD Functionality for Calculations

## 📋 Project Overview

This project extends the JWT-authenticated FastAPI calculator application with complete **BREAD (Browse, Read, Edit, Add, Delete)** functionality for calculation data. It includes comprehensive Playwright E2E tests covering all BREAD operations, a full CI/CD pipeline with GitHub Actions, and Docker deployment ready for production.

## 🎯 Key Features

- ✅ **BREAD Operations** - Full Browse, Read, Edit, Add, Delete for calculations
- ✅ **JWT Authentication** - Secure token-based authentication
- ✅ **User Registration** - Email and username validation with password hashing
- ✅ **User Login** - Credential verification and JWT token generation
- ✅ **Front-End Dashboard** - Interactive HTML interface for BREAD operations
- ✅ **Playwright E2E Tests** - 3 comprehensive browser automation tests (all passing ✓)
- ✅ **CI/CD Pipeline** - Automated testing and Docker Hub deployment via GitHub Actions
- ✅ **Code Coverage** - 125+ passing Python unit/integration tests
- ✅ **venv Python Support** - All tests and CI/CD use virtualenv Python

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+ (for Playwright)
- Git
- (Optional) Docker & Docker Compose

### Installation

```bash
# Clone the repository
git clone https://github.com/Pruthul15/assignment14.git
cd assignment14

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies (for Playwright)
npm install
npx playwright install
```

## 🧪 Running Tests

### Python Unit & Integration Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all Python tests
pytest -q

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=term-missing
```

### Playwright E2E Tests

#### Option 1: Using the helper script (Recommended - uses venv Python)

```bash
# Start server (with venv Python) and run Playwright tests
npm run e2e

# Run single test (pass any Playwright args after --)
npm run e2e -- tests/e2e/bread-calculation.spec.js:120 --reporter=list
```

#### Option 2: Manual (separate terminals)

Terminal 1 - Start FastAPI server:
```bash
source venv/bin/activate
./venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Terminal 2 - Run Playwright tests:
```bash
npx playwright test tests/e2e/bread-calculation.spec.js --reporter=list --workers=1
```

### Test Results Summary

**Python Tests:** 125+ passing (pytest)
- Unit tests for auth, models, schemas
- Integration tests for API endpoints
- Database tests for CRUD operations

**Playwright E2E Tests:** 3 passing (100%)
- ✓ Register → Login (positive + negative scenarios)
- ✓ Add, browse, read, edit, delete calculations (positive flows)
- ✓ Invalid inputs and unauthorized access (negative scenarios)

## 🐳 Running with Docker

### Start the Application

```bash
# Build and start containers
docker-compose up -d

# Wait for services to start
sleep 5

# Verify app is running
curl http://localhost:8001/health
```

### Access the Application

- **Home Page:** http://localhost:8001/
- **Register:** http://localhost:8001/register
- **Login:** http://localhost:8001/login
- **Dashboard:** http://localhost:8001/dashboard (requires login)
- **API Docs:** http://localhost:8001/docs

### Stop the Application

```bash
docker-compose down
```

## 🍞 BREAD Operations

### Browse (GET /calculations)
Retrieve all calculations for the authenticated user.

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8001/calculations
```

**Response:**
```json
[
  {
    "id": "uuid",
    "type": "addition",
    "inputs": [7, 3],
    "result": 10,
    "created_at": "2025-11-23T12:00:00Z"
  }
]
```

### Read (GET /calculations/{id})
Retrieve details of a specific calculation.

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8001/calculations/uuid
```

### Add (POST /calculations)
Create a new calculation.

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type": "addition", "inputs": [7, 3]}' \
  http://localhost:8001/calculations
```

### Edit (PUT /calculations/{id})
Update an existing calculation's inputs.

```bash
curl -X PUT \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"inputs": [8, 2]}' \
  http://localhost:8001/calculations/uuid
```

### Delete (DELETE /calculations/{id})
Remove a calculation.

```bash
curl -X DELETE \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8001/calculations/uuid
```

## 🔐 API Endpoints

### Authentication

#### Register New User
```bash
POST /auth/register
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!"
}
```

#### Login
```bash
POST /auth/login
Content-Type: application/json

{
  "username": "newuser",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_at": "2025-11-23T12:30:00Z",
  "user_id": "uuid",
  "username": "newuser",
  "email": "user@example.com"
}
```

## 🧑‍💻 Using the Web Dashboard

### Register
1. Go to http://localhost:8001/register
2. Fill in form with valid credentials
3. Click Register → redirects to login page

### Login
1. Go to http://localhost:8001/login
2. Enter username and password
3. Click Sign in → redirects to dashboard

### Dashboard - Add Calculation
1. Select operation type (Addition, Subtraction, Multiplication, Division)
2. Enter numbers (comma-separated)
3. Click Calculate
4. Result appears in history table

### Dashboard - Browse/View
- All your calculations appear in the history table
- Click "View" to see calculation details

### Dashboard - Edit
1. Click "Edit" on any calculation
2. Modify the numbers
3. Click Update
4. Result is recalculated automatically

### Dashboard - Delete
1. Click "Delete" on any calculation
2. Confirm deletion
3. Calculation is removed from history

## 📊 Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI, SQLAlchemy, SQLite/PostgreSQL |
| **Frontend** | Jinja2, HTML5, CSS3, JavaScript |
| **Authentication** | JWT (HS256), bcrypt |
| **E2E Testing** | Playwright (JavaScript) |
| **Python Testing** | pytest, pytest-cov |
| **DevOps** | Docker, Docker Compose, GitHub Actions |
| **Package Mgmt** | pip (Python), npm (Node.js) |

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow (`.github/workflows/ci.yml`)

Runs automatically on push to `main` branch:

1. **Setup** (30 sec)
   - Python 3.11 + Node.js 20
   - Install dependencies

2. **Start FastAPI App** (10 sec)
   - Uvicorn runs on 127.0.0.1:8001
   - Tables created on startup
   - Health check verifies server

3. **Run Python Tests** (30 sec)
   - `pytest -q` runs all unit/integration tests

4. **Run Playwright E2E Tests** (60 sec)
   - `npx playwright test` runs all 3 E2E tests
   - Headless mode, single worker
   - 60-second timeout per test

5. **Docker Build & Push** (90 sec, requires secrets)
   - Build image: `pruthul123/assignment14:COMMIT_SHA`
   - Push with tags: `:latest` and `:COMMIT_SHA`
   - **Requires secrets:**
     - `DOCKERHUB_USERNAME`
     - `DOCKERHUB_TOKEN`

**View workflow:** https://github.com/Pruthul15/assignment14/actions

### Set Up Docker Hub Secrets

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add `DOCKERHUB_USERNAME` = your Docker Hub username
4. Add `DOCKERHUB_TOKEN` = your Docker Hub access token (generate in Docker Hub settings)

## 🐳 Docker Hub

Docker image is automatically pushed to:
- **Repository:** https://hub.docker.com/r/pruthul123/assignment14
- **Tags:**
  - `latest` - Most recent build
  - `<git-sha>` - Specific commit version

### Pull and Run Image

```bash
# Pull the image
docker pull pruthul123/assignment14:latest

# Run the image
docker run -p 8001:8001 \
  -e DATABASE_URL="sqlite:///./test.db" \
  -e JWT_SECRET_KEY="your-secret-key" \
  pruthul123/assignment14:latest
```

## 📁 Project Structure

```
assignment14/
├── app/
│   ├── auth/              # Authentication logic
│   │   ├── jwt.py        # JWT token generation
│   │   ├── dependencies.py # Auth middleware
│   │   └── redis.py      # Token blacklisting (optional)
│   ├── models/
│   │   ├── user.py       # User model with auth methods
│   │   └── calculation.py # Calculation model (polymorphic)
│   ├── schemas/
│   │   ├── user.py       # Pydantic user schemas
│   │   ├── token.py      # Token schemas
│   │   └── calculation.py # Calculation schemas
│   ├── core/
│   │   └── config.py     # Configuration
│   ├── database.py       # Database setup
│   ├── database_init.py  # Table initialization
│   └── main.py           # FastAPI app with BREAD endpoints
├── templates/
│   ├── register.html     # Registration page
│   ├── login.html        # Login page
│   ├── dashboard.html    # Dashboard (protected, BREAD UI)
│   ├── view_calculation.html
│   ├── edit_calculation.html
│   ├── delete_calculation.html
│   ├── layout.html       # Base template
│   └── index.html        # Home page
├── static/
│   └── css/
│       └── style.css     # Styling
├── tests/
│   ├── unit/            # Unit tests
│   ├── integration/      # Integration tests
│   ├── e2e/             # Playwright E2E tests (3 passing)
│   │   └── bread-calculation.spec.js
│   └── conftest.py      # Pytest configuration
├── scripts/
│   └── run_e2e.sh       # Helper to run E2E tests with venv Python
├── .github/
│   └── workflows/
│       └── ci.yml       # GitHub Actions CI/CD
├── docker-compose.yml    # Multi-container setup
├── Dockerfile           # Docker image
├── playwright.config.js  # Playwright configuration
├── package.json         # npm scripts (e2e, test)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🔒 Security Features

- ✅ **Password Hashing** - bcrypt with salt
- ✅ **JWT Tokens** - HS256 algorithm with 30-min expiration
- ✅ **Protected Routes** - Dependency injection for auth checks
- ✅ **SQL Injection Prevention** - SQLAlchemy parameterized queries
- ✅ **User-Specific Data** - Calculations filtered by user_id

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Check what's using port 8001
lsof -i :8001

# Kill process (if needed)
kill -9 <PID>

# Or use a different port
./venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8002
```

### Playwright Tests Timeout

```bash
# Ensure server is running first
./venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8001

# Then run tests with higher timeout
npx playwright test tests/e2e/bread-calculation.spec.js --timeout=120000
```

### Tests Failing with "Target page closed"

```bash
# Kill any lingering processes
pkill -f uvicorn
pkill -f playwright

# Clean up and restart
rm -rf .pytest_cache test-results/
npm run e2e
```

## 📝 Environment Variables

For local development (optional `.env` file):

```env
DATABASE_URL=sqlite:///./test.db
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_REFRESH_SECRET_KEY=your-refresh-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## ✅ Assignment Requirements Met

### 1. BREAD Endpoints ✅
- ✅ Browse: `GET /calculations` - list all user's calculations
- ✅ Read: `GET /calculations/{id}` - get specific calculation
- ✅ Edit: `PUT /calculations/{id}` - update calculation inputs
- ✅ Add: `POST /calculations` - create new calculation
- ✅ Delete: `DELETE /calculations/{id}` - remove calculation

### 2. Front-End Functionality ✅
- ✅ Dashboard with add/edit/delete forms
- ✅ Client-side validation for numeric inputs
- ✅ Calculation history table with actions
- ✅ Toast alerts for success/error

### 3. Playwright E2E Tests ✅
- ✅ Test 1: Register → Login (positive + negative)
- ✅ Test 2: Add, browse, read, edit, delete (positive flows)
- ✅ Test 3: Invalid inputs, unauthorized access (negative)
- ✅ All 3 tests passing ✓

### 4. CI/CD Integration ✅
- ✅ GitHub Actions workflow for pytest + Playwright
- ✅ Docker image build and push to Docker Hub
- ✅ Automated testing on every push
- ✅ Uses venv Python for consistency

### 5. Documentation ✅
- ✅ This README with full instructions
- ✅ REFLECTION.md with challenges/experiences
- ✅ Inline code comments in key files
- ✅ API endpoint documentation

## 🚀 Quick Start Summary

```bash
# 1. Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
npm install
npx playwright install

# 2. Test Python
pytest -q

# 3. Test E2E (start server + run Playwright)
npm run e2e

# 4. Run locally
./venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
# Visit http://localhost:8001
```

## 👤 Author

- **Name:** Pruthul Patel
- **GitHub:** https://github.com/Pruthul15
- **Docker Hub:** https://hub.docker.com/u/pruthul123

## 📄 License

MIT License - See LICENSE file for details

## 🔗 Links

- **GitHub Repository:** https://github.com/Pruthul15/assignment14
- **Docker Hub Repository:** https://hub.docker.com/r/pruthul123/assignment14
- **GitHub Actions:** https://github.com/Pruthul15/assignment14/actions
- **API Documentation:** http://localhost:8001/docs (when running locally)

---

**Status:** ✅ All BREAD operations implemented, all E2E tests passing, CI/CD pipeline ready

