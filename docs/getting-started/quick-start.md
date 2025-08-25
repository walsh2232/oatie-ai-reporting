# Quick Start Guide

Get up and running with Oatie in under 5 minutes!

## Prerequisites

Before you begin, ensure you have:

- **Docker & Docker Compose** installed
- **OpenAI API Key** (for AI features)
- **Oracle Database access** (optional, for testing)

## 🚀 Option 1: Docker Compose (Recommended)

The fastest way to get started is using Docker Compose:

### 1. Clone the Repository

```bash
git clone https://github.com/username/oatie.git
cd oatie
```

### 2. Configure Environment

```bash
# Copy environment templates
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit backend/.env with your settings
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./oatie.db
LOG_LEVEL=INFO
```

### 3. Start the Application

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### 4. Access the Application

- **Frontend**: http://localhost:5174
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🛠️ Option 2: Manual Setup

For development or customization:

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🎯 First Steps

### 1. Create an Account

1. Open http://localhost:5174 in your browser
2. Click "Sign Up" or use demo credentials:
   - **Username**: `demo@oatie.ai`
   - **Password**: `demo123`

### 2. Connect to Oracle (Optional)

1. Navigate to the Dashboard
2. Click "Add Oracle Connection"
3. Fill in your Oracle database details:
   - **Host**: Your Oracle server hostname
   - **Port**: 1521 (default)
   - **Service Name**: Your Oracle service name
   - **Username/Password**: Your credentials

### 3. Try Your First Query

1. Go to the "Query" tab
2. Enter a natural language query:
   ```
   Show me all employees hired in the last 30 days
   ```
3. Click "Generate SQL"
4. Review the generated SQL query
5. Execute or refine as needed

## 📊 Example Queries

Try these example queries to see Oatie in action:

### Basic Queries
- "Show all customers from California"
- "List products with price greater than 100"
- "Count orders by month for this year"

### Advanced Queries
- "Show top 10 sales representatives by revenue"
- "Calculate average order value by customer segment"
- "Find customers who haven't ordered in 90 days"

### Oracle BI Publisher Specific
- "Generate a quarterly sales report"
- "Create a customer aging report"
- "Show inventory levels by location"

## 🔧 Configuration

### Environment Variables

#### Backend Configuration
```bash
# Required
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=sqlite:///./oatie.db

# Optional
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:5174
MAX_QUERY_LENGTH=1000
CACHE_TTL=3600
```

#### Frontend Configuration
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_ENVIRONMENT=development
VITE_APP_NAME=Oatie
```

### OpenAI Configuration

1. Get an API key from [OpenAI](https://platform.openai.com/)
2. Add it to your `backend/.env` file
3. Restart the backend service

### Oracle Connection

Oatie supports various Oracle connection methods:
- **Direct Connection**: Host, port, service name
- **TNS Connection**: TNS names configuration
- **Oracle Cloud**: Cloud connection strings

## 🧪 Testing the Setup

### Health Checks

```bash
# Check backend health
curl http://localhost:8000/health

# Check if services are running
docker-compose ps
```

### Sample API Calls

```bash
# Get table metadata
curl -X GET "http://localhost:8000/api/metadata/tables"

# Test SQL generation
curl -X POST "http://localhost:8000/api/sql/generate" \
  -H "Content-Type: application/json" \
  -d '{"query": "show all customers", "table_name": "customers"}'
```

## 🚨 Troubleshooting

### Common Issues

#### Docker Issues
```bash
# Reset Docker environment
docker-compose down -v
docker-compose up -d --build
```

#### Database Issues
```bash
# Reset database
cd backend
rm oatie.db
alembic upgrade head
```

#### Permission Issues (Linux/Mac)
```bash
# Fix permissions
sudo chown -R $USER:$USER .
```

### Log Analysis

```bash
# View backend logs
docker-compose logs backend

# View frontend logs
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f
```

## 📚 Next Steps

Now that you have Oatie running:

1. **[Configuration Guide](configuration.md)** - Detailed configuration options
2. **[Oracle Integration](../oracle/connection-setup.md)** - Connect to your Oracle BI Publisher
3. **[User Guide](../user-guides/dashboard.md)** - Learn the interface
4. **[API Documentation](../api/README.md)** - Integrate with your applications

## 💬 Getting Help

- **Documentation**: Browse our [complete documentation](../README.md)
- **GitHub Issues**: [Report bugs or request features](https://github.com/username/oatie/issues)
- **Community**: [Join our discussions](https://github.com/username/oatie/discussions)
- **Email**: [team@oatie.ai](mailto:team@oatie.ai)

---

**🎉 Congratulations!** You now have Oatie running and ready to transform your Oracle BI Publisher workflows with AI assistance.
