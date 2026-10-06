# AI Trip Planner - Deployment Guide

This guide provides instructions for deploying the AI Trip Planner application to production.

## Prerequisites

Before deploying, ensure you have:

1. **API Keys and Services**:
   - Supabase project with database setup
   - SERP API key for travel data
   - Google Gemini API key for AI content generation

2. **Environment Setup**:
   - Node.js 18+ for frontend
   - Python 3.11+ for backend
   - Production server or cloud platform

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# External API Keys
SERP_API_KEY=your_serp_api_key
GEMINI_API_KEY=your_gemini_api_key

# JWT Configuration (IMPORTANT: Change in production!)
SECRET_KEY=your_secure_jwt_secret_key_minimum_32_characters

# Production Settings
ENVIRONMENT=production
DEBUG=false
```

### Security Notes

- **SECRET_KEY**: Must be at least 32 characters long and cryptographically secure
- **API Keys**: Keep all API keys secure and never commit them to version control
- **Database**: Ensure Supabase RLS (Row Level Security) is properly configured

## Database Setup

1. **Create Supabase Project**:
   - Go to [Supabase](https://supabase.com) and create a new project
   - Note down your project URL and anon key

2. **Run Database Migrations**:
   ```bash
   cd backend
   python database_migrations.py
   ```

3. **Verify Tables**:
   - Check that `users` and `trip_plans` tables are created
   - Verify foreign key relationships are in place

## Production Build

### Automated Build (Recommended)

Use the provided build scripts:

**Linux/macOS**:
```bash
chmod +x scripts/build-prod.sh
./scripts/build-prod.sh
```

**Windows**:
```cmd
scripts\build-prod.bat
```

### Manual Build

If you prefer to build manually:

1. **Backend Setup**:
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m pytest tests/ -v  # Run tests
   ```

2. **Frontend Build**:
   ```bash
   cd frontend
   npm ci
   npm test -- --run  # Run tests
   npm run build
   ```

## Deployment Options

### Option 1: Cloud Platforms (Recommended)

#### Vercel (Frontend) + Railway/Render (Backend)

**Frontend (Vercel)**:
1. Connect your GitHub repository to Vercel
2. Set build command: `cd frontend && npm run build`
3. Set output directory: `frontend/dist`
4. Configure environment variables in Vercel dashboard

**Backend (Railway/Render)**:
1. Connect your GitHub repository
2. Set start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Configure environment variables in platform dashboard

#### Netlify (Frontend) + Heroku (Backend)

**Frontend (Netlify)**:
1. Connect repository to Netlify
2. Set build command: `cd frontend && npm run build`
3. Set publish directory: `frontend/dist`

**Backend (Heroku)**:
1. Create `Procfile` in backend directory:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
2. Deploy using Heroku CLI or GitHub integration

### Option 2: VPS/Dedicated Server

#### Using Docker (Recommended)

1. **Create Dockerfile for Backend**:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY backend/requirements.txt .
   RUN pip install -r requirements.txt
   COPY backend/ .
   EXPOSE 8000
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Create Dockerfile for Frontend**:
   ```dockerfile
   FROM node:18-alpine as build
   WORKDIR /app
   COPY frontend/package*.json ./
   RUN npm ci
   COPY frontend/ .
   RUN npm run build
   
   FROM nginx:alpine
   COPY --from=build /app/dist /usr/share/nginx/html
   EXPOSE 80
   CMD ["nginx", "-g", "daemon off;"]
   ```

3. **Docker Compose**:
   ```yaml
   version: '3.8'
   services:
     backend:
       build:
         context: .
         dockerfile: Dockerfile.backend
       ports:
         - "8000:8000"
       environment:
         - SUPABASE_URL=${SUPABASE_URL}
         - SUPABASE_KEY=${SUPABASE_KEY}
         - SERP_API_KEY=${SERP_API_KEY}
         - GEMINI_API_KEY=${GEMINI_API_KEY}
         - SECRET_KEY=${SECRET_KEY}
     
     frontend:
       build:
         context: .
         dockerfile: Dockerfile.frontend
       ports:
         - "80:80"
       depends_on:
         - backend
   ```

#### Manual Server Setup

1. **Install Dependencies**:
   ```bash
   # Install Node.js and Python
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs python3 python3-pip nginx
   ```

2. **Deploy Backend**:
   ```bash
   # Copy backend files to server
   cd /var/www/ai-trip-planner/backend
   pip3 install -r requirements.txt
   
   # Create systemd service
   sudo nano /etc/systemd/system/ai-trip-planner.service
   ```

3. **Configure Nginx**:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           root /var/www/ai-trip-planner/frontend/dist;
           try_files $uri $uri/ /index.html;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## Post-Deployment Checklist

- [ ] All environment variables are set correctly
- [ ] Database migrations have been run
- [ ] API endpoints are accessible
- [ ] Frontend loads without errors
- [ ] Authentication flow works
- [ ] Trip planning functionality works
- [ ] External API integrations work (SERP, Gemini)
- [ ] Error handling works properly
- [ ] HTTPS is configured (for production)
- [ ] Monitoring and logging are set up

## Monitoring and Maintenance

### Health Checks

The application provides a health check endpoint:
```
GET /health
```

### Logs

Monitor application logs for:
- API errors
- Database connection issues
- External API failures
- Authentication problems

### Performance

- Monitor API response times
- Check database query performance
- Monitor external API usage and limits

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Verify Supabase URL and key
   - Check network connectivity
   - Ensure database tables exist

2. **API Key Issues**:
   - Verify all API keys are valid
   - Check API usage limits
   - Ensure keys have proper permissions

3. **Build Failures**:
   - Check Node.js and Python versions
   - Verify all dependencies are installed
   - Check for syntax errors in code

4. **CORS Issues**:
   - Ensure backend CORS is configured for frontend domain
   - Check that API URLs are correct

### Support

For deployment issues:
1. Check the application logs
2. Verify environment variables
3. Test API endpoints individually
4. Check external service status

## Security Considerations

- Use HTTPS in production
- Implement rate limiting
- Keep dependencies updated
- Monitor for security vulnerabilities
- Use environment variables for all secrets
- Enable Supabase RLS policies
- Implement proper error handling to avoid information leakage