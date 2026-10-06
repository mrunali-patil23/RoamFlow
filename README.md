# AI-Powered Real-Time Trip Planner

A full-stack web application that provides intelligent travel planning capabilities by integrating real-time travel data from SERP API, AI-generated content from Gemini API, and persistent storage through Supabase.

## 🚀 Features

- **Secure Authentication**: User registration and login with JWT tokens
- **Real-Time Travel Data**: Flights, hotels, attractions, events, and weather via SERP API
- **AI-Generated Content**: Smart descriptions and travel tips via Gemini API
- **Cost Management**: Detailed cost breakdowns and budget tracking in ₹ INR
- **Day-by-Day Itineraries**: Structured travel plans with activities and costs
- **Data Persistence**: Save and compare multiple trip plans
- **Offline Support**: Access last generated itinerary without internet
- **Export & Sharing**: PDF export and shareable trip links
- **Responsive UI**: Light/dark mode with skeleton loaders

## 🏗️ Architecture

### Frontend
- **React.js** with TypeScript
- **Tailwind CSS** for styling
- **Vite** for development and building
- **React Router** for navigation

### Backend
- **Python FastAPI** for REST API
- **Supabase** for database and authentication
- **SERP API** for real-time travel data
- **Gemini API** for AI content generation

### Database
- **PostgreSQL** via Supabase
- User management and trip plan storage
- Relational data with proper constraints

## 📋 Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- Supabase account
- SERP API key
- Gemini API key

## 🛠️ Setup Instructions

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd ai-trip-planner

# Copy environment variables
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` file with your actual API keys:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# External API Keys
SERP_API_KEY=your_serp_api_key
GEMINI_API_KEY=your_gemini_api_key

# JWT Configuration
SECRET_KEY=your_jwt_secret_key_change_in_production
```

### 3. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend server
python main.py
```

The backend will be available at `http://localhost:8000`

### 4. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 🧪 Running Tests

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📚 API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## 🔑 Default Credentials

For testing purposes, default admin credentials are available:
- **Username**: admin
- **Password**: admin123

## 🏃‍♂️ Development Scripts

### Frontend
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm test` - Run tests

### Backend
- `python main.py` - Start FastAPI server
- `pytest` - Run tests
- `pytest --cov` - Run tests with coverage

## 📁 Project Structure

```
ai-trip-planner/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── utils/          # Utility functions
│   │   └── types/          # TypeScript types
│   ├── public/             # Static assets
│   └── package.json
├── backend/                 # Python FastAPI backend
│   ├── models/             # Data models
│   ├── services/           # Business logic
│   ├── routers/            # API routes
│   ├── tests/              # Test files
│   ├── main.py             # FastAPI app
│   ├── config.py           # Configuration
│   ├── database.py         # Database connection
│   └── requirements.txt
├── .env.example            # Environment variables template
└── README.md
```

## 🔧 Configuration

### API Keys Required

1. **Supabase**: Create a project at [supabase.com](https://supabase.com)
2. **SERP API**: Get API key from [serpapi.com](https://serpapi.com)
3. **Gemini API**: Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Database Schema

The application will automatically create the required database tables:
- `users` - User authentication data
- `trip_plans` - Saved trip plans
- `itineraries` - Day-by-day itinerary data
- `cost_breakdowns` - Cost analysis data

## 🚀 Deployment

### Quick Deployment with Docker (Recommended)

1. **Set up environment variables**:
   ```bash
   cp .env.production .env
   # Edit .env with your production API keys
   ```

2. **Deploy using the deployment script**:
   ```bash
   # Linux/macOS
   ./scripts/deploy.sh docker production
   
   # Windows
   scripts\deploy.bat docker production
   ```

3. **Access your application**:
   - Frontend: http://localhost
   - Backend API: http://localhost:8000

### Manual Production Build

Use the production build scripts:

```bash
# Linux/macOS
./scripts/build-prod.sh

# Windows
scripts\build-prod.bat
```

### Cloud Platform Deployment

#### Frontend (Vercel/Netlify)
1. Connect your repository to Vercel or Netlify
2. Set build command: `cd frontend && npm run build`
3. Set output directory: `frontend/dist`
4. Configure environment variables in platform dashboard

#### Backend (Railway/Render/Heroku)
1. Connect your repository to your preferred platform
2. Set start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Configure environment variables in platform dashboard

### Docker Deployment

The project includes Docker configuration for containerized deployment:

```bash
# Development
docker-compose up --build

# Production
docker-compose -f docker-compose.prod.yml up --build -d
```

### Environment Variables for Production

Ensure these variables are set in production:

```env
SUPABASE_URL=your_production_supabase_url
SUPABASE_KEY=your_production_supabase_key
SERP_API_KEY=your_serp_api_key
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_secure_production_secret_key
ENVIRONMENT=production
DEBUG=false
```

**Security Note**: Use a strong, unique SECRET_KEY (minimum 32 characters) in production.

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
1. Check the API documentation at `/docs`
2. Review the test files for usage examples
3. Open an issue for bugs or feature requests

---

Built with ❤️ using React, FastAPI, and Supabase