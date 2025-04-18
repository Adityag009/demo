# BNI Yellow Pages API (app.py)

This README explains the FastAPI implementation for the BNI Yellow Pages system. The API serves as the interface between the frontend application and the backend services, handling member and visitor registration, report generation, and status tracking.

## Table of Contents

- [Overview](#overview)
- [API Endpoints](#api-endpoints)
- [Backend Workflow](#backend-workflow)
- [Component Integration](#component-integration)
- [Authentication (Future)](#authentication-future)
- [Error Handling](#error-handling)
- [Installation & Configuration](#installation--configuration)

## Overview

The `app.py` file implements a FastAPI application that serves as the central hub for all client interactions with the BNI Yellow Pages system. It coordinates:

1. User data collection (members and visitors)
2. AI-powered business analysis 
3. Report generation and delivery
4. Status tracking for async operations

## API Endpoints

### Health Check
- `GET /` - Verify the API is running

### Member Management
- `POST /members` - Register a new BNI member

### Visitor Management
- `POST /visitors` - Register a new BNI visitor

### Report Generation
- `POST /reports/generate` - Trigger report generation (asynchronous)
- `GET /reports/{user_type}/{user_id}/latest` - Get status and URL of latest report

## Backend Workflow

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI (app.py)
    participant DB as MongoDB
    participant Analysis as Analysis Services
    participant S3 as S3 Storage
    
    %% Member/Visitor Registration
    Client->>API: POST /members or /visitors
    API->>DB: save_member() or save_visitor()
    DB-->>API: user_id
    API-->>Client: { id, status: "success" }
    
    %% Report Generation
    Client->>API: POST /reports/generate
    API->>DB: Verify user exists
    DB-->>API: User data
    API->>DB: Save "pending" status
    API-->>Client: { status: "pending" }
    
    %% Background Processing (Async)
    Note over API,Analysis: Background Task
    API->>DB: get_parameters_mongodb()
    DB-->>API: User parameters
    
    API->>Analysis: generate_ai_strategy()
    Analysis-->>API: AI strategy
    
    API->>Analysis: identify_revenue_opportunities()
    Analysis-->>API: Revenue opportunities
    
    alt Member report
        API->>Analysis: recommend_bni_connections()
        Analysis-->>API: BNI connections
        
        API->>Analysis: recommend_gains_contactsphere_matches()
        Analysis-->>API: GAINS matches
        
        API->>Analysis: optimize_profile()
        Analysis-->>API: Profile optimization
    end
    
    API->>Analysis: generate_report()
    Analysis-->>API: PDF content
    
    API->>S3: upload_pdf()
    S3-->>API: report_url
    
    API->>DB: save_report_metadata()
    API->>DB: update_analysis_results()
    
    %% Status Checking
    Client->>API: GET /reports/{user_type}/{user_id}/latest
    API->>DB: get_visitor() or get_member()
    DB-->>API: User data with reports
    API-->>Client: { report_url, status }
    
    %% Report Access
    Client->>S3: GET report_url
    S3-->>Client: PDF Report
```

## Component Integration

The API integrates several components:

### Data Models (`models.py`)
- Pydantic models for request validation
- Strongly typed interfaces for database operations
- Response models for consistent API outputs

### Database Services (`database.py`/`database1.py`)
- MongoDB data persistence
- User data retrieval and management
- Report metadata tracking

### Storage Services (`s3_service.py`)
- PDF report storage on AWS S3 or local filesystem
- Presigned URL generation for secure access
- Test environment support

### Analysis Services
- AI strategy generation
- Revenue opportunity identification
- BNI connection recommendations
- Profile optimization

## Backend Processing Flow

1. **Data Collection**
   - Client submits member/visitor data via API
   - Data is validated using Pydantic models
   - Validated data is stored in MongoDB

2. **Report Generation** (Asynchronous)
   - Client requests report generation with user ID
   - API records pending status in database
   - Background task begins processing
   - API immediately returns response to client

3. **Analysis Pipeline** (Background)
   - Retrieve user data from MongoDB
   - Generate AI strategy based on business info
   - Identify revenue opportunities
   - For members: Generate BNI recommendations and GAINS matches
   - Create PDF report with all analysis components
   - Upload PDF to S3 storage
   - Update database with report URL and status

4. **Report Delivery**
   - Client polls status endpoint
   - When report is ready, client receives S3 URL
   - Client retrieves PDF report directly from S3

## Error Handling

The API implements comprehensive error handling:

- **Database Errors**: Captured and logged with specific error messages
- **Processing Errors**: Recorded in the database for tracking
- **HTTP Exceptions**: Custom handlers ensure consistent response format
- **Unhandled Exceptions**: Global handler prevents raw error exposure

Error responses follow a consistent format:
```json
{
  "detail": "Error message",
  "status": "error"
}
```

## Installation & Configuration

### Requirements
- Python 3.8+
- FastAPI
- MongoDB
- AWS S3 access (or local storage for testing)

### Environment Variables
```
# API Configuration
ALLOWED_ORIGINS=https://example.com,https://app.example.com

# MongoDB Configuration
MONGODB_URI=mongodb://username:password@localhost:27017/
MONGODB_DB_NAME=bni_yellow_pages

# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=bni-reports

# Environment Mode
ENV=production  # or "test" for local storage
LOCAL_STORAGE_PATH=~/bni_reports  # Only used in test mode
```

### Running the API
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app:app --reload

# Run production server
uvicorn app:app --host 0.0.0.0 --port 8000
```

### API Documentation
FastAPI automatically generates interactive documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Future Enhancements

- **Authentication**: Implement JWT authentication for secure API access
- **Rate Limiting**: Add rate limiting to prevent abuse
- **Webhooks**: Notify clients when reports are complete
- **Caching**: Implement caching for frequently accessed data
- **Monitoring**: Add detailed performance metrics and monitoring
