# API Documentation Standards

## Overview

This document establishes standards for API documentation, including OpenAPI specifications, documentation generation, and maintenance procedures for the Oatie platform.

## Documentation Standards

### 1. OpenAPI Specification

#### OpenAPI Version
We use **OpenAPI 3.0.3** for all API documentation.

#### Basic Structure
```yaml
openapi: 3.0.3
info:
  title: Oatie API
  description: |
    Oatie AI reporting platform API for Oracle BI Publisher integration.
    
    ## Authentication
    All endpoints require authentication via JWT Bearer token.
    
    ## Rate Limiting
    API calls are limited to 1000 requests per hour per user.
    
    ## Error Handling
    The API uses standard HTTP status codes and returns detailed error messages.
  version: 1.0.0
  termsOfService: https://oatie.ai/terms
  contact:
    name: Oatie API Support
    url: https://oatie.ai/support
    email: api-support@oatie.ai
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: https://api.oatie.ai/v1
    description: Production server
  - url: https://staging-api.oatie.ai/v1
    description: Staging server
  - url: http://localhost:8000/v1
    description: Development server

security:
  - bearerAuth: []

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

### 2. Schema Definitions

#### Common Models
```yaml
components:
  schemas:
    User:
      type: object
      required:
        - id
        - email
        - firstName
        - lastName
      properties:
        id:
          type: string
          format: uuid
          description: Unique user identifier
          example: "123e4567-e89b-12d3-a456-426614174000"
        email:
          type: string
          format: email
          description: User's email address
          example: "user@example.com"
        username:
          type: string
          minLength: 3
          maxLength: 30
          pattern: '^[a-zA-Z0-9_-]+$'
          description: Unique username
          example: "john_doe"
        firstName:
          type: string
          maxLength: 100
          description: User's first name
          example: "John"
        lastName:
          type: string
          maxLength: 100
          description: User's last name
          example: "Doe"
        organizationId:
          type: string
          format: uuid
          description: Organization the user belongs to
        role:
          type: string
          enum: [super_admin, org_admin, report_manager, report_viewer, user]
          description: User's role in the organization
        isActive:
          type: boolean
          description: Whether the user account is active
        createdAt:
          type: string
          format: date-time
          description: When the user was created
        updatedAt:
          type: string
          format: date-time
          description: When the user was last updated
        lastLogin:
          type: string
          format: date-time
          description: User's last login time
          nullable: true

    Report:
      type: object
      required:
        - id
        - name
        - templateId
        - status
      properties:
        id:
          type: string
          format: uuid
          description: Unique report identifier
        name:
          type: string
          maxLength: 255
          description: Report name
          example: "Monthly Sales Report"
        description:
          type: string
          description: Report description
          example: "Comprehensive sales analysis for the current month"
        templateId:
          type: string
          format: uuid
          description: Template used for this report
        organizationId:
          type: string
          format: uuid
          description: Organization that owns the report
        createdBy:
          type: string
          format: uuid
          description: User who created the report
        parameters:
          type: object
          description: Report parameters and filters
          additionalProperties: true
        configuration:
          type: object
          description: Report configuration options
          additionalProperties: true
        status:
          type: string
          enum: [draft, scheduled, processing, completed, failed, cancelled]
          description: Current status of the report
        priority:
          type: integer
          minimum: 1
          maximum: 10
          description: Report execution priority
        scheduledAt:
          type: string
          format: date-time
          description: When the report is scheduled to run
          nullable: true
        createdAt:
          type: string
          format: date-time
          description: When the report was created
        updatedAt:
          type: string
          format: date-time
          description: When the report was last updated
        lastExecuted:
          type: string
          format: date-time
          description: When the report was last executed
          nullable: true

    Error:
      type: object
      required:
        - error
        - message
      properties:
        error:
          type: string
          description: Error code
          example: "VALIDATION_ERROR"
        message:
          type: string
          description: Human-readable error message
          example: "The request contains invalid data"
        details:
          type: object
          description: Additional error details
          additionalProperties: true
        timestamp:
          type: string
          format: date-time
          description: When the error occurred
        requestId:
          type: string
          description: Unique request identifier for debugging

    PaginationResponse:
      type: object
      required:
        - data
        - pagination
      properties:
        data:
          type: array
          description: Array of items
        pagination:
          type: object
          required:
            - page
            - limit
            - total
            - totalPages
          properties:
            page:
              type: integer
              minimum: 1
              description: Current page number
            limit:
              type: integer
              minimum: 1
              maximum: 100
              description: Number of items per page
            total:
              type: integer
              minimum: 0
              description: Total number of items
            totalPages:
              type: integer
              minimum: 0
              description: Total number of pages
            hasNext:
              type: boolean
              description: Whether there is a next page
            hasPrevious:
              type: boolean
              description: Whether there is a previous page
```

### 3. Endpoint Documentation

#### Standard Endpoint Format
```yaml
paths:
  /reports:
    get:
      summary: List reports
      description: |
        Retrieve a paginated list of reports for the authenticated user's organization.
        
        ## Permissions
        Requires `reports:view` permission.
        
        ## Filters
        - `status`: Filter by report status
        - `templateId`: Filter by template
        - `createdBy`: Filter by creator
        
        ## Sorting
        Default sort is by `createdAt` descending. Supported sort fields:
        - `name` (ascending/descending)
        - `createdAt` (ascending/descending)
        - `updatedAt` (ascending/descending)
        - `lastExecuted` (ascending/descending)
      operationId: listReports
      tags:
        - Reports
      parameters:
        - name: page
          in: query
          description: Page number (1-based)
          required: false
          schema:
            type: integer
            minimum: 1
            default: 1
        - name: limit
          in: query
          description: Number of items per page
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
        - name: status
          in: query
          description: Filter by report status
          required: false
          schema:
            type: string
            enum: [draft, scheduled, processing, completed, failed, cancelled]
        - name: templateId
          in: query
          description: Filter by template ID
          required: false
          schema:
            type: string
            format: uuid
        - name: createdBy
          in: query
          description: Filter by creator user ID
          required: false
          schema:
            type: string
            format: uuid
        - name: sort
          in: query
          description: Sort field and direction
          required: false
          schema:
            type: string
            enum: [name:asc, name:desc, createdAt:asc, createdAt:desc, updatedAt:asc, updatedAt:desc]
            default: createdAt:desc
        - name: search
          in: query
          description: Search in report names and descriptions
          required: false
          schema:
            type: string
            maxLength: 255
      responses:
        '200':
          description: List of reports retrieved successfully
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/PaginationResponse'
                  - type: object
                    properties:
                      data:
                        type: array
                        items:
                          $ref: '#/components/schemas/Report'
              examples:
                success:
                  summary: Successful response
                  value:
                    data:
                      - id: "123e4567-e89b-12d3-a456-426614174000"
                        name: "Monthly Sales Report"
                        description: "Sales analysis for current month"
                        templateId: "456e7890-e89b-12d3-a456-426614174000"
                        status: "completed"
                        createdAt: "2024-01-15T10:30:00Z"
                        updatedAt: "2024-01-15T10:30:00Z"
                    pagination:
                      page: 1
                      limit: 20
                      total: 45
                      totalPages: 3
                      hasNext: true
                      hasPrevious: false
        '400':
          description: Bad request - invalid parameters
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              examples:
                invalidPage:
                  summary: Invalid page number
                  value:
                    error: "VALIDATION_ERROR"
                    message: "Page number must be greater than 0"
                    timestamp: "2024-01-15T10:30:00Z"
                    requestId: "req_123456789"
        '401':
          $ref: '#/components/responses/Unauthorized'
        '403':
          $ref: '#/components/responses/Forbidden'
        '500':
          $ref: '#/components/responses/InternalServerError'

    post:
      summary: Create a new report
      description: |
        Create a new report based on a template.
        
        ## Permissions
        Requires `reports:create` permission.
        
        ## Validation
        - Report name must be unique within the organization
        - Template must exist and be accessible
        - Parameters must match template requirements
      operationId: createReport
      tags:
        - Reports
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - name
                - templateId
              properties:
                name:
                  type: string
                  maxLength: 255
                  description: Report name
                description:
                  type: string
                  description: Report description
                templateId:
                  type: string
                  format: uuid
                  description: Template to use for the report
                parameters:
                  type: object
                  description: Report parameters
                  additionalProperties: true
                configuration:
                  type: object
                  description: Report configuration
                  additionalProperties: true
                scheduledAt:
                  type: string
                  format: date-time
                  description: Schedule the report for future execution
            examples:
              basic:
                summary: Basic report creation
                value:
                  name: "Q1 Sales Analysis"
                  description: "Quarterly sales performance analysis"
                  templateId: "456e7890-e89b-12d3-a456-426614174000"
                  parameters:
                    dateRange:
                      start: "2024-01-01"
                      end: "2024-03-31"
                    regions: ["North", "South"]
              scheduled:
                summary: Scheduled report
                value:
                  name: "Weekly Status Report"
                  templateId: "789e0123-e89b-12d3-a456-426614174000"
                  scheduledAt: "2024-01-22T09:00:00Z"
      responses:
        '201':
          description: Report created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Report'
        '400':
          description: Bad request - validation failed
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '409':
          description: Conflict - report name already exists
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
```

### 4. Response Standards

#### Standard Response Formats
```yaml
components:
  responses:
    Unauthorized:
      description: Authentication required
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "UNAUTHORIZED"
            message: "Authentication required"
            timestamp: "2024-01-15T10:30:00Z"
            requestId: "req_123456789"

    Forbidden:
      description: Insufficient permissions
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "FORBIDDEN"
            message: "Insufficient permissions to access this resource"
            timestamp: "2024-01-15T10:30:00Z"
            requestId: "req_123456789"

    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "NOT_FOUND"
            message: "The requested resource was not found"
            timestamp: "2024-01-15T10:30:00Z"
            requestId: "req_123456789"

    InternalServerError:
      description: Internal server error
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "INTERNAL_ERROR"
            message: "An unexpected error occurred"
            timestamp: "2024-01-15T10:30:00Z"
            requestId: "req_123456789"
```

## Documentation Generation

### 1. Automated Generation

#### TypeScript/Node.js
```typescript
// src/swagger.ts
import swaggerJsdoc from 'swagger-jsdoc';
import swaggerUi from 'swagger-ui-express';
import { Express } from 'express';

const options = {
  definition: {
    openapi: '3.0.3',
    info: {
      title: 'Oatie API',
      version: '1.0.0',
      description: 'Oatie AI reporting platform API',
    },
    servers: [
      {
        url: process.env.API_BASE_URL || 'http://localhost:8000/v1',
        description: 'API Server',
      },
    ],
  },
  apis: ['./src/routes/*.ts', './src/models/*.ts'],
};

const specs = swaggerJsdoc(options);

export function setupSwagger(app: Express): void {
  app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(specs, {
    explorer: true,
    customCss: '.swagger-ui .topbar { display: none }',
    customSiteTitle: 'Oatie API Documentation',
  }));
}
```

#### Python/FastAPI
```python
# main.py
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Oatie API",
    description="Oatie AI reporting platform API",
    version="1.0.0",
    docs_url="/api-docs",
    redoc_url="/api-redoc",
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Oatie API",
        version="1.0.0",
        description="Oatie AI reporting platform API",
        routes=app.routes,
    )
    
    # Add custom information
    openapi_schema["info"]["contact"] = {
        "name": "Oatie API Support",
        "url": "https://oatie.ai/support",
        "email": "api-support@oatie.ai",
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Example endpoint with documentation
@app.get(
    "/reports",
    response_model=PaginatedReportResponse,
    summary="List reports",
    description="Retrieve a paginated list of reports",
    tags=["Reports"],
)
async def list_reports(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[ReportStatus] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
):
    """
    List reports for the authenticated user's organization.
    
    - **page**: Page number (starting from 1)
    - **limit**: Number of items per page (1-100)
    - **status**: Filter by report status
    
    Returns a paginated list of reports with metadata.
    """
    # Implementation here
    pass
```

### 2. Documentation Validation

#### OpenAPI Validation Script
```python
#!/usr/bin/env python3
"""
OpenAPI specification validator
"""

import yaml
import json
from openapi_spec_validator import validate_spec
from openapi_spec_validator.readers import read_from_filename

def validate_openapi_spec(spec_file: str):
    """Validate OpenAPI specification"""
    try:
        spec_dict = read_from_filename(spec_file)
        validate_spec(spec_dict)
        print(f"✅ {spec_file} is valid")
        return True
    except Exception as e:
        print(f"❌ {spec_file} validation failed: {e}")
        return False

def check_required_fields(spec_dict: dict):
    """Check for required documentation fields"""
    errors = []
    
    # Check info section
    info = spec_dict.get('info', {})
    required_info = ['title', 'version', 'description', 'contact']
    for field in required_info:
        if field not in info:
            errors.append(f"Missing required info field: {field}")
    
    # Check paths have descriptions
    paths = spec_dict.get('paths', {})
    for path, methods in paths.items():
        for method, details in methods.items():
            if 'description' not in details:
                errors.append(f"Missing description for {method.upper()} {path}")
            if 'summary' not in details:
                errors.append(f"Missing summary for {method.upper()} {path}")
    
    return errors

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: validate_openapi.py <spec_file>")
        sys.exit(1)
    
    spec_file = sys.argv[1]
    
    # Validate spec
    if not validate_openapi_spec(spec_file):
        sys.exit(1)
    
    # Check additional requirements
    with open(spec_file, 'r') as f:
        spec_dict = yaml.safe_load(f)
    
    errors = check_required_fields(spec_dict)
    if errors:
        print("❌ Documentation requirements not met:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    print("✅ All documentation requirements met")
```

### 3. Documentation Testing

#### API Contract Testing
```python
# tests/test_api_contract.py
import pytest
import requests
from schemathesis import from_dict
from openapi_spec_validator.readers import read_from_filename

class TestAPIContract:
    @pytest.fixture
    def api_schema(self):
        return read_from_filename('docs/openapi.yaml')
    
    @pytest.fixture
    def schemathesis_schema(self, api_schema):
        return from_dict(api_schema)
    
    def test_openapi_spec_valid(self, api_schema):
        """Test that OpenAPI spec is valid"""
        from openapi_spec_validator import validate_spec
        validate_spec(api_schema)
    
    def test_all_endpoints_documented(self, api_schema):
        """Test that all endpoints are documented"""
        # Get actual endpoints from application
        response = requests.get('http://localhost:8000/routes')
        actual_routes = response.json()
        
        # Get documented endpoints
        documented_paths = set(api_schema['paths'].keys())
        
        # Check coverage
        missing_docs = set(actual_routes) - documented_paths
        assert not missing_docs, f"Undocumented endpoints: {missing_docs}"
    
    @pytest.mark.parametrize("endpoint", [
        "/reports",
        "/templates",
        "/users",
    ])
    def test_endpoint_examples_valid(self, api_schema, endpoint):
        """Test that endpoint examples are valid"""
        path_spec = api_schema['paths'][endpoint]
        
        for method, spec in path_spec.items():
            examples = spec.get('requestBody', {}).get('content', {}).get('application/json', {}).get('examples', {})
            
            for example_name, example in examples.items():
                # Validate example against schema
                schema = spec['requestBody']['content']['application/json']['schema']
                # Add validation logic here
                pass
```

## Documentation Maintenance

### 1. Automated Updates

#### GitHub Actions Workflow
```yaml
name: API Documentation

on:
  push:
    branches: [main, develop]
    paths: ['src/**/*.ts', 'src/**/*.py', 'docs/openapi.yaml']
  pull_request:
    paths: ['src/**/*.ts', 'src/**/*.py', 'docs/openapi.yaml']

jobs:
  validate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Validate OpenAPI Spec
        run: |
          pip install openapi-spec-validator
          python scripts/validate_openapi.py docs/openapi.yaml
      
      - name: Generate Documentation
        run: |
          npm install -g redoc-cli
          redoc-cli build docs/openapi.yaml --output docs/api/index.html
      
      - name: Test API Contracts
        run: |
          pip install schemathesis
          pytest tests/test_api_contract.py
      
      - name: Deploy Documentation
        if: github.ref == 'refs/heads/main'
        run: |
          # Deploy to documentation site
          aws s3 sync docs/api/ s3://docs.oatie.ai/api/
```

### 2. Documentation Review Process

#### Review Checklist
```markdown
## API Documentation Review Checklist

### Completeness
- [ ] All endpoints documented
- [ ] All parameters described
- [ ] All response codes covered
- [ ] Examples provided for complex requests
- [ ] Error responses documented

### Accuracy
- [ ] Request/response schemas match implementation
- [ ] Examples are valid and realistic
- [ ] Status codes are correct
- [ ] Authentication requirements specified

### Clarity
- [ ] Clear, concise descriptions
- [ ] Technical terms explained
- [ ] Use cases provided where helpful
- [ ] Permissions requirements stated

### Standards Compliance
- [ ] Follows OpenAPI 3.0.3 specification
- [ ] Consistent naming conventions
- [ ] Standard HTTP methods used appropriately
- [ ] Proper use of status codes
```

### 3. Version Management

#### API Versioning Strategy
```yaml
# Version 1.0
paths:
  /v1/reports:
    get:
      # Current stable version

# Version 2.0 (breaking changes)
paths:
  /v2/reports:
    get:
      # New version with breaking changes

# Deprecated version
paths:
  /reports:
    get:
      deprecated: true
      description: |
        **DEPRECATED**: This endpoint is deprecated. 
        Use `/v1/reports` instead.
        Will be removed in version 3.0.
```

#### Changelog Generation
```python
#!/usr/bin/env python3
"""
Generate API changelog from OpenAPI specs
"""

import yaml
from deepdiff import DeepDiff

def generate_changelog(old_spec_file: str, new_spec_file: str):
    """Generate changelog between two OpenAPI specs"""
    
    with open(old_spec_file, 'r') as f:
        old_spec = yaml.safe_load(f)
    
    with open(new_spec_file, 'r') as f:
        new_spec = yaml.safe_load(f)
    
    diff = DeepDiff(old_spec, new_spec, ignore_order=True)
    
    changelog = []
    
    # New endpoints
    new_paths = diff.get('dictionary_item_added', [])
    for path in new_paths:
        if path.startswith("root['paths']"):
            endpoint = path.split("'")[3]
            changelog.append(f"➕ **Added**: New endpoint `{endpoint}`")
    
    # Removed endpoints
    removed_paths = diff.get('dictionary_item_removed', [])
    for path in removed_paths:
        if path.startswith("root['paths']"):
            endpoint = path.split("'")[3]
            changelog.append(f"🗑️ **Removed**: Endpoint `{endpoint}`")
    
    # Modified endpoints
    changed_values = diff.get('values_changed', {})
    for path, change in changed_values.items():
        if "paths" in path:
            changelog.append(f"🔄 **Modified**: {path}")
    
    return "\n".join(changelog)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: generate_changelog.py <old_spec> <new_spec>")
        sys.exit(1)
    
    changelog = generate_changelog(sys.argv[1], sys.argv[2])
    print("## API Changes\n")
    print(changelog)
```

This comprehensive API documentation standard ensures that all APIs are well-documented, maintainable, and provide an excellent developer experience.