# Technology Stack Steering Document

## Architecture

### System Design
- **Microservices Architecture**: フロントエンド、バックエンドAPI、AI処理を分離
- **Event-Driven Processing**: 非同期での画像・動画生成処理
- **Serverless Functions**: AI処理をCloud Functionsで実行
- **Container-Based Deployment**: Cloud Runでのサービスデプロイ

### Infrastructure Platform
- **Cloud Provider**: Google Cloud Platform (GCP)
- **Infrastructure as Code**: Terraform (implemented)
- **Container Runtime**: Cloud Run (planned)
- **Function Runtime**: Cloud Functions (planned)
- **State Management**: GCS backend for Terraform (optional)

## Frontend

### Core Technologies
- **Language**: TypeScript
- **Framework**: React 18+
- **Build Tool**: Next.js (App Router)
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **State Management**: Jotai (if needed)

### Frontend Libraries (Implemented)
```json
{
  "dependencies": {
    "react": "^18",
    "react-dom": "^18",
    "next": "14.2.16",
    "tailwindcss": "^4.1.9",
    "@radix-ui/react-*": "various versions",
    "lucide-react": "^0.454.0",
    "react-hook-form": "^7.60.0",
    "zod": "3.25.67",
    "sonner": "^1.7.4",
    "next-themes": "^0.4.6",
    "class-variance-authority": "^0.7.1",
    "tailwind-merge": "^2.5.5"
  }
}
```

## Backend

### Core Technologies
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **ASGI Server**: Uvicorn
- **Package Manager**: uv (not pip/venv)

### Backend Libraries
```python
# Current dependencies (from pyproject.toml)
fastapi>=0.116.2        # Web framework (implemented)
uvicorn>=0.35.0         # ASGI server (implemented)
pydantic>=2.11.9        # Data validation
pydantic-settings>=2.10.1  # Settings management
python-dotenv>=1.1.1    # Environment management
google-cloud-storage>=3.4.0  # GCS client
google-generativeai     # Gemini AI client (implemented in services)

# Development dependencies
black>=25.1.0           # Code formatter
ruff>=0.13.0            # Linter
mypy>=1.18.1            # Type checker
pytest>=8.4.2           # Testing framework
pytest-asyncio>=1.2.0   # Async testing
pytest-cov>=7.0.0       # Test coverage
pytest-mock>=3.15.1     # Mocking support
httpx>=0.28.1           # HTTP client for testing
```

## AI Models

### Image Generation
- **Model**: Gemini 2.5 Flash Image Preview (Nano Banana)
- **API**: Google Generative AI
- **Deployment**: Cloud Functions
- **Input**: Face photo + prompt
- **Output**: Styled makeup images

### Video Generation
- **Model**: Veo 3.0 Generate 001
- **API**: Google Generative AI
- **Deployment**: Cloud Functions
- **Input**: Image + instruction text
- **Output**: 10-second tutorial videos
- **Polling**: 10-second intervals

### Text Processing
- **Model**: Gemini (Structured Output mode)
- **Usage**:
  - Makeup procedure structuring
  - Step decomposition
  - Instruction generation
- **Output Format**: Structured JSON with title, description, steps, tools

## Development Environment

### Required Tools
- **Node.js**: v18+ (for frontend)
- **Python**: 3.11+ (for backend and functions)
- **uv**: Python package manager
- **gcloud CLI**: GCP management
- **terraform**: Infrastructure provisioning

### Code Quality Tools
- **Python**: black, ruff, mypy
- **TypeScript**: ESLint, Prettier
- **Git Hooks**: Pre-commit validation

## Common Commands

### Frontend Development
```bash
cd apps/web
npm install         # Install dependencies
npm run dev        # Start development server
npm run build      # Production build
npm run format     # Format code
npm run lint       # Lint code
```

### Backend Development
```bash
cd apps/api
uv sync            # Install dependencies
uv run fastapi dev # Start development server
uv run black .     # Format Python code
uv run ruff check  # Lint Python code
uv run mypy .      # Type check
uv run pytest      # Run tests
```

### Infrastructure
```bash
cd terraform/environments/dev
terraform init     # Initialize Terraform
terraform plan     # Preview changes
terraform apply    # Apply infrastructure
terraform destroy  # Tear down resources
```

## Environment Variables

### Backend/Functions (.env)
```env
GOOGLE_API_KEY=<Gemini API key>
GOOGLE_CLOUD_PROJECT=<GCP project ID>
STORAGE_BUCKET=<GCS bucket name>
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=<Backend API URL>
NEXT_PUBLIC_STORAGE_URL=<GCS public URL>
```

## Port Configuration

### Development Ports
- **Frontend (Next.js)**: 3000
- **Backend (FastAPI)**: 8000
- **Cloud Functions**: Deployed URLs

### Service URLs (Production)
- **Frontend**: https://<project>-web-<hash>.run.app
- **Backend**: https://<project>-api-<hash>.run.app
- **Functions**: https://<region>-<project>.cloudfunctions.net/<function>

## Storage Solutions

### Google Cloud Storage
- **Purpose**: Image and video storage
- **Buckets**:
  - User uploads
  - Generated images
  - Generated videos
- **Access**: Service account authentication

### Database (If Needed)
- **Service**: Cloud SQL (PostgreSQL)
- **Purpose**: Session data, processing status
- **Alternative**: Firestore for NoSQL needs

## Security Considerations

### API Security
- **CORS Configuration**: Frontend domain only
- **API Keys**: Environment variables only
- **Service Accounts**: Least privilege principle
- **Secrets Management**: Google Secret Manager (future)

### Data Privacy
- **User Data**: Temporary storage only (demo)
- **Image Processing**: No permanent storage of faces
- **GDPR/Privacy**: Not implemented (demo)

## Performance Optimization

### Frontend
- **Image Optimization**: Next.js Image component
- **Lazy Loading**: Component-level code splitting
- **Caching**: Browser caching for static assets

### Backend
- **Async Processing**: FastAPI async endpoints
- **Connection Pooling**: Database connections
- **Response Caching**: CDN for static content

### AI Processing
- **Batch Processing**: Not implemented (demo)
- **Queue Management**: Not implemented (demo)
- **Retry Logic**: Simple exponential backoff

## Monitoring (Future)

### Observability Stack
- **Logging**: Cloud Logging
- **Metrics**: Cloud Monitoring
- **Tracing**: Cloud Trace
- **Error Tracking**: Cloud Error Reporting