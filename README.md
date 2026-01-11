# AI Travel Planner

A full-stack web application that creates personalized travel itineraries using artificial intelligence and real-time transport data.

## Technology Stack

### Frontend
- **Next.js 15** with App Router
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **React Hooks** for state management

### Backend
- **FastAPI** with Python
- **Pydantic** for data validation
- **Google Gemini AI** for itinerary generation
- **Amadeus API** for flight data
- **Supabase/MongoDB** for data persistence

## Project Structure

```
ai-travel-planner/
├── frontend/                 # Next.js frontend application
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   ├── components/      # React components
│   │   ├── lib/            # Utilities and API client
│   │   └── types/          # TypeScript type definitions
│   └── package.json
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── models/         # Pydantic models
│   │   └── services/       # Business logic services
│   ├── tests/              # Backend tests
│   ├── main.py             # FastAPI application entry point
│   └── requirements.txt
└── package.json            # Root package.json with scripts
```

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-travel-planner
   ```

2. **Install all dependencies**
   ```bash
   npm run install:all
   ```

3. **Set up environment variables**
   
   **Backend (.env):**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your API keys
   ```
   
   **Frontend (.env.local):**
   ```bash
   cp frontend/.env.local.example frontend/.env.local
   # Edit frontend/.env.local with your configuration
   ```

4. **Start the development servers**
   ```bash
   npm run dev
   ```
   
   This will start:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000

### Individual Services

**Frontend only:**
```bash
npm run dev:frontend
```

**Backend only:**
```bash
npm run dev:backend
```

## API Documentation

Once the backend is running, visit:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Development Scripts

- `npm run dev` - Start both frontend and backend
- `npm run dev:frontend` - Start frontend only
- `npm run dev:backend` - Start backend only
- `npm run build` - Build frontend for production
- `npm run install:all` - Install all dependencies

## Features

- **AI-Powered Planning**: Uses Google Gemini AI to generate personalized itineraries
- **Real-time Transport**: Integration with Amadeus API for flight data
- **Modern UI**: Clean, responsive design with Tailwind CSS
- **Type Safety**: Full TypeScript support across frontend and backend
- **Scalable Architecture**: Modular design with clear separation of concerns

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.