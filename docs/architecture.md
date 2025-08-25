# 🏗️ Architecture Guide

## Overview

Oatie AI Reporting is built with a modern microservices architecture that separates concerns between the AI-powered backend and the interactive frontend, with Oracle BI Publisher integration at its core.

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Frontend      │◄──►│   Backend       │◄──►│ Oracle BI       │
│   (React/TS)    │    │   (FastAPI)     │    │ Publisher       │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   User          │    │   AI Services   │    │   Database      │
│   Interface     │    │   (OpenAI)      │    │   (SQLite/      │
│                 │    │                 │    │    PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Component Architecture

### Frontend (React/TypeScript)

```
frontend/src/
├── components/          # Reusable UI components
│   ├── common/         # Common components (buttons, inputs, etc.)
│   ├── layout/         # Layout components (header, footer, sidebar)
│   └── reporting/      # Reporting-specific components
├── pages/              # Page-level components
│   ├── dashboard/      # Dashboard and overview pages
│   ├── reports/        # Report management pages
│   └── settings/       # Configuration pages
├── hooks/              # Custom React hooks
├── services/           # API communication services
├── types/              # TypeScript type definitions
├── utils/              # Utility functions
└── test/               # Test utilities and setup
```

**Key Technologies:**
- **React 18**: Modern React with hooks and concurrent features
- **TypeScript**: Type safety and developer experience
- **Vite**: Fast build tool and development server
- **Oracle Redwood**: Oracle's design system for consistency
- **React Query**: Server state management
- **Zustand**: Client state management
- **React Hook Form**: Form management with validation

### Backend (Python/FastAPI)

```
backend/oatie/
├── api/                # API route handlers
│   ├── v1/            # API version 1 endpoints
│   │   ├── reports/   # Report management endpoints
│   │   ├── ai/        # AI-powered features endpoints
│   │   └── auth/      # Authentication endpoints
│   └── dependencies/  # Dependency injection
├── core/              # Core functionality
│   ├── config.py     # Configuration management
│   ├── security.py   # Security utilities
│   └── database.py   # Database connection
├── models/            # Database models
│   ├── user.py       # User models
│   ├── report.py     # Report models
│   └── audit.py      # Audit trail models
├── services/          # Business logic services
│   ├── ai_service.py  # AI integration service
│   ├── oracle_service.py # Oracle BI Publisher service
│   └── report_service.py # Report management service
└── utils/             # Utility functions
    ├── validators.py  # Input validation
    └── helpers.py     # Common helpers
```

**Key Technologies:**
- **FastAPI**: Modern, fast web framework with automatic API docs
- **SQLAlchemy**: Object-relational mapping with async support
- **Alembic**: Database migration management
- **Pydantic**: Data validation and serialization
- **OAuth2/JWT**: Secure authentication
- **OpenAI API**: AI-powered features

## Data Flow

### 1. User Request Flow

```
User Action → Frontend → API Gateway → Backend Service → Database/Oracle → Response
```

### 2. AI-Powered Report Generation

```
User Input → Frontend → Backend → AI Service → Oracle BI Publisher → Generated Report
```

### 3. Real-time Updates

```
Database Change → Event → WebSocket → Frontend Update
```

## Security Architecture

### Authentication & Authorization

- **OAuth2 with JWT**: Secure token-based authentication
- **Role-Based Access Control (RBAC)**: Fine-grained permissions
- **API Key Management**: Secure handling of external service keys

### Data Protection

- **Encryption at Rest**: Sensitive data encrypted in database
- **TLS 1.3**: All communications encrypted in transit
- **Input Validation**: Comprehensive validation on all inputs
- **SQL Injection Prevention**: Parameterized queries and ORM

### Security Headers

```http
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Strict-Transport-Security: max-age=31536000
```

## Database Design

### Core Entities

```sql
Users
├── id (UUID, Primary Key)
├── username (String, Unique)
├── email (String, Unique)
├── hashed_password (String)
├── role (Enum: admin, user, viewer)
└── created_at (DateTime)

Reports
├── id (UUID, Primary Key)
├── name (String)
├── description (Text)
├── oracle_report_id (String)
├── created_by (UUID, Foreign Key -> Users.id)
├── ai_generated (Boolean)
└── created_at (DateTime)

AuditLogs
├── id (UUID, Primary Key)
├── user_id (UUID, Foreign Key -> Users.id)
├── action (String)
├── resource_type (String)
├── resource_id (UUID)
└── timestamp (DateTime)
```

## Integration Architecture

### Oracle BI Publisher Integration

```python
class OracleService:
    async def generate_report(self, template_id: str, data: dict) -> Report:
        # Connect to Oracle BI Publisher
        # Apply AI-generated parameters
        # Execute report generation
        # Return formatted report
```

### AI Service Integration

```python
class AIService:
    async def generate_report_config(self, user_input: str) -> ReportConfig:
        # Process natural language input
        # Generate Oracle BI Publisher configuration
        # Validate configuration
        # Return structured config
```

## Deployment Architecture

### Development Environment

```yaml
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    depends_on: [backend]
  
  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [database]
  
  database:
    image: postgres:15
    environment:
      POSTGRES_DB: oatie
```

### Production Environment

```
Load Balancer → Frontend (Static Files) → CDN
             → Backend (API) → Database Cluster
                            → Redis Cache
                            → External Services (Oracle, OpenAI)
```

## Performance Considerations

### Caching Strategy

- **Browser Cache**: Static assets cached for 1 year
- **API Cache**: Redis cache for frequent queries (5-60 minutes)
- **Database Cache**: Query result caching for complex reports

### Scalability

- **Horizontal Scaling**: Stateless backend services
- **Database Scaling**: Read replicas for reporting queries
- **CDN**: Global content delivery for frontend assets

## Monitoring & Observability

### Metrics Collection

- **Application Metrics**: Response times, error rates, throughput
- **Business Metrics**: Report generation success rates, user activity
- **Infrastructure Metrics**: CPU, memory, disk usage

### Logging Strategy

```python
import structlog

logger = structlog.get_logger()
logger.info("Report generated", 
    user_id=user.id, 
    report_id=report.id, 
    duration_ms=duration
)
```

### Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": await check_database(),
        "oracle": await check_oracle_connection(),
        "ai_service": await check_ai_service()
    }
```

## Development Workflow

### Local Development

1. **Setup**: `docker-compose up -d` (database, Redis)
2. **Backend**: `uvicorn main:app --reload`
3. **Frontend**: `npm run dev`
4. **Testing**: `pytest` (backend), `npm test` (frontend)

### CI/CD Pipeline

```yaml
Quality Gates:
├── Code Formatting (Black, Prettier)
├── Linting (Pylint, ESLint)
├── Type Checking (MyPy, TypeScript)
├── Security Scanning (Bandit, npm audit)
├── Testing (pytest, vitest)
└── Coverage (>90% required)
```

## API Design

### RESTful Endpoints

```
GET    /api/v1/reports          # List reports
POST   /api/v1/reports          # Create report
GET    /api/v1/reports/{id}     # Get report
PUT    /api/v1/reports/{id}     # Update report
DELETE /api/v1/reports/{id}     # Delete report

POST   /api/v1/ai/generate      # AI-powered generation
GET    /api/v1/health           # Health check
```

### WebSocket Events

```
connect    -> authentication
subscribe  -> report_updates:{report_id}
message    -> report_progress, report_complete
disconnect -> cleanup
```

## Future Architecture Considerations

### Microservices Evolution

As the application grows, consider splitting into:
- **User Service**: Authentication and user management
- **Report Service**: Report generation and management
- **AI Service**: AI-powered features
- **Notification Service**: Real-time updates and notifications

### Event-Driven Architecture

Implement event sourcing for audit trails and eventual consistency:
```
Command → Event Store → Event Handlers → Read Models
```

---

This architecture provides a solid foundation that can scale with the application's growth while maintaining security, performance, and maintainability standards.