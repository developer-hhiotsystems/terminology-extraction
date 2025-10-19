# Getting Started with Glossary APP

Welcome to the Glossary APP! This guide will help you get up and running quickly.

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- Git

### Installation & Startup

#### Option 1: Automated Startup (Recommended)
```batch
# Start both backend and frontend servers
scripts\startup\START-ALL-SERVERS.bat
```

#### Option 2: Manual Startup
```batch
# Terminal 1 - Backend
scripts\startup\START-BACKEND.bat

# Terminal 2 - Frontend
scripts\startup\START-FRONTEND.bat
```

### Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:9123
- API Health Check: http://localhost:9123/health

## Next Steps

After starting the servers:

1. **Upload Documents**: Navigate to the upload page to add your glossary documents
2. **Browse Terms**: Explore extracted terms and definitions
3. **Search**: Use the FTS5-powered search (10.6x faster!)
4. **Explore Relationships**: View the knowledge graph visualization

## Troubleshooting

See [START-AFTER-RESTART.md](./START-AFTER-RESTART.md) for detailed startup instructions.

For testing procedures, see [../operations/TESTING_PROCEDURE.md](../operations/TESTING_PROCEDURE.md).

## Documentation

- **Features**: See [../features/](../features/) for feature documentation
- **Architecture**: See [../architecture/](../architecture/) for system design docs
- **Operations**: See [../operations/](../operations/) for deployment and monitoring guides
