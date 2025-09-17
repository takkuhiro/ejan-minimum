# Project Structure Steering Document

## Root Directory Organization

```
ejan-minimum/
├── .claude/               # Claude Code configuration
│   ├── commands/         # Custom slash commands
│   └── settings.json     # Tool permissions and preferences
├── .kiro/                # Spec-driven development
│   ├── steering/        # Project steering documents
│   └── specs/          # Feature specifications
├── apps/                # Monorepo applications
│   ├── api/            # Backend API service (implemented)
│   ├── web/            # Frontend web application (implemented)
│   └── functions/      # Cloud Functions (planned)
├── docs/                # Project documentation
│   ├── PRODUCT.md      # Product requirements
│   └── agents/         # Agent implementation docs
├── terraform/           # Infrastructure as code (implemented)
│   ├── environments/   # Environment configurations
│   ├── modules/       # Terraform modules
│   └── README.md      # Infrastructure documentation
├── CLAUDE.md           # Claude Code context
└── README.md           # Project overview (planned)
```

## Subdirectory Structures

### Frontend Structure (apps/web) - Implemented
```
apps/web/
├── app/                 # Next.js App Router
│   ├── layout.tsx      # Root layout
│   ├── page.tsx        # Home/Welcome page
│   ├── globals.css     # Global styles
│   ├── styles/         # Style selection page
│   │   └── page.tsx
│   ├── customize/      # Style customization page
│   │   └── page.tsx
│   ├── generating/     # Loading/generation page
│   │   └── page.tsx
│   └── tutorial/       # Tutorial steps page
│       └── page.tsx
├── components/          # React components
│   ├── ui/            # shadcn/ui components (50+ components)
│   ├── photo-upload.tsx # Photo upload component
│   └── theme-provider.tsx # Dark mode support
├── lib/                # Utilities and helpers
│   └── utils.ts       # Common utilities (cn function)
├── hooks/              # Custom React hooks
│   ├── use-toast.ts   # Toast notifications
│   └── use-mobile.ts  # Mobile detection
├── public/             # Static assets
├── package.json        # Dependencies
├── tsconfig.json       # TypeScript config
├── next.config.mjs     # Next.js config
├── tailwind.config.ts  # Tailwind config
└── components.json     # shadcn/ui config
```

### Backend Structure (apps/api) - Current State
```
apps/api/
├── samples/           # AI model integration examples
│   ├── image_generation_with_nano_banana.py
│   └── video_generation_with_veo3.py
├── app/                # FastAPI application (implemented)
│   ├── main.py        # Application entry point (implemented)
│   ├── __init__.py    # Package initialization
│   ├── core/          # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py  # Configuration (implemented)
│   │   └── storage.py # Storage clients (implemented)
│   ├── models/        # Data models
│   │   ├── __init__.py
│   │   ├── request.py # Request schemas (implemented)
│   │   └── response.py# Response schemas (implemented)
│   └── services/      # Business logic
│       ├── __init__.py
│       ├── storage.py # Storage service (implemented)
│       ├── ai_client.py # Gemini AI client (implemented)
│       ├── image_generation.py # Nano Banana service (implemented)
│       └── tutorial_structure.py # Tutorial generation (implemented)
├── tests/             # Test files (implemented)
│   ├── __init__.py
│   ├── unit/         # Unit tests
│   │   ├── __init__.py
│   │   ├── test_config.py
│   │   ├── test_models.py
│   │   ├── test_storage_client.py
│   │   ├── test_storage_service.py
│   │   ├── test_ai_client.py
│   │   ├── test_image_generation.py
│   │   └── test_tutorial_structure.py
│   └── integration/  # Integration tests
│       ├── __init__.py
│       └── test_app_setup.py
├── pyproject.toml     # Python project config (implemented)
├── .env              # Environment variables
└── Dockerfile        # Container definition (planned)
```

### Cloud Functions Structure (apps/functions) - Planned
```
apps/functions/        # Not yet implemented
├── image_generation/    # Nano Banana function
│   ├── main.py        # Function entry point
│   ├── requirements.txt
│   └── deploy.yaml    # Deployment config
├── video_generation/    # Veo3 function
│   ├── main.py        # Function entry point
│   ├── requirements.txt
│   └── deploy.yaml    # Deployment config
└── shared/             # Shared utilities
    └── clients.py     # Shared API clients
```

### Infrastructure Structure (terraform) - Implemented
```
terraform/
├── environments/      # Environment configs
│   └── dev/          # Development environment
│       ├── main.tf   # Main configuration
│       ├── variables.tf  # Variable definitions
│       └── outputs.tf    # Output definitions
├── modules/          # Terraform modules
│   ├── iam/         # IAM configuration
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── storage/     # GCS buckets
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── README.md        # Infrastructure documentation
```

## Code Organization Patterns

### Component Organization (Frontend)
- **Atomic Design**: atoms → molecules → organisms
- **Feature-Based**: Group by feature, not file type
- **Co-location**: Keep related files together
- **Barrel Exports**: Use index.ts for clean imports

### Service Organization (Backend)
- **Layer Separation**: Routes → Services → Models
- **Dependency Injection**: Use FastAPI dependencies
- **Domain-Driven**: Organize by business domain
- **Repository Pattern**: Abstract data access

### Function Organization (Cloud Functions)
- **Single Responsibility**: One function, one task
- **Minimal Dependencies**: Keep functions lightweight
- **Error Handling**: Comprehensive error responses
- **Idempotency**: Handle retries gracefully

## File Naming Conventions

### TypeScript/JavaScript
- **Components**: PascalCase (e.g., `UserProfile.tsx`)
- **Utilities**: camelCase (e.g., `formatDate.ts`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)
- **Types**: PascalCase with suffix (e.g., `UserType.ts`)

### Python
- **Modules**: snake_case (e.g., `image_processor.py`)
- **Classes**: PascalCase (e.g., `ImageGenerator`)
- **Functions**: snake_case (e.g., `generate_image()`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_FILE_SIZE`)

### General
- **Config Files**: lowercase with extension (e.g., `config.json`)
- **Documentation**: UPPERCASE or Title Case (e.g., `README.md`)
- **Environment**: dotenv format (e.g., `.env`, `.env.local`)
- **Test Files**: mirror source with suffix (e.g., `user.test.ts`)

## Import Organization

### TypeScript Imports
```typescript
// 1. External dependencies
import React from 'react';
import { useState } from 'react';

// 2. Internal aliases
import { Button } from '@/components/ui';
import { api } from '@/lib/api';

// 3. Relative imports
import { UserCard } from './UserCard';
import styles from './styles.module.css';
```

### Python Imports
```python
# 1. Standard library
import os
from typing import Optional

# 2. Third-party
from fastapi import FastAPI
from pydantic import BaseModel

# 3. Local application
from app.core import config
from app.services import image_service
```

## Key Architectural Principles

### Frontend Principles
- **Server-Side Rendering**: Use Next.js SSR when possible
- **Client-Side Hydration**: Minimize JavaScript payload
- **Component Reusability**: Build composable components
- **Type Safety**: Leverage TypeScript strictly

### Backend Principles
- **API-First Design**: Design APIs before implementation
- **Async by Default**: Use async/await for I/O operations
- **Schema Validation**: Use Pydantic for data validation
- **Service Layer**: Separate business logic from routes

### Infrastructure Principles
- **Infrastructure as Code**: Everything in Terraform
- **Environment Parity**: Dev/staging/prod consistency
- **Least Privilege**: Minimal permissions for services
- **Immutable Infrastructure**: Replace, don't modify

### Testing Principles
- **Test-Driven Development**: Write tests first
- **Test Isolation**: Each test independent
- **Coverage Goals**: 80% minimum coverage
- **Test Categories**: Unit, Integration, E2E

## Module Boundaries

### Clear Separation
- **Frontend ↔ Backend**: REST API only
- **Backend ↔ Functions**: Async messaging
- **Functions ↔ Storage**: Direct GCS access
- **All Services ↔ External APIs**: Client libraries

### Shared Code Policy
- **No Cross-App Imports**: Apps are independent
- **Shared Types**: Duplicate if needed
- **Common Utils**: Copy, don't share
- **Configuration**: Environment-based

## Implementation Notes

### Current State (as of update)
- **Frontend**: Fully implemented with mock data (5 pages)
- **Backend**: FastAPI structure implemented with storage, AI, and generation services
- **AI Services**: Gemini integration, image generation, and tutorial structure services implemented
- **Cloud Functions**: Sample implementations ready, deployment pending
- **Infrastructure**: Terraform modules for storage and IAM implemented

### Next Implementation Steps
1. **Backend API Endpoints**: Complete style generation and tutorial endpoints integration
2. **Cloud Functions**: Deploy implemented Nano Banana and Veo3 functions
3. **Integration**: Connect frontend to backend API
4. **Cloud Run Deployment**: Deploy backend and frontend to Cloud Run
5. **Testing**: Complete end-to-end integration tests

## Development Workflow

### Branch Strategy
- **main**: Production-ready code
- **develop**: Integration branch
- **feature/***: Feature development
- **fix/***: Bug fixes

### Commit Conventions
```
feat: Add user upload functionality
fix: Resolve image processing error
docs: Update API documentation
test: Add unit tests for image service
refactor: Simplify video generation logic
```

### Code Review Requirements
- **Type Safety**: No any types
- **Test Coverage**: Include tests
- **Documentation**: Update relevant docs
- **Performance**: Consider implications