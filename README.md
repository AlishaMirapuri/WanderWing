# WanderWing

An LLM-powered travel companion matching platform that connects travelers going to the same destination using agentic workflows and intelligent compatibility scoring.

## Features

- **Smart Itinerary Parsing**: Convert natural language travel plans into structured data
- **Intelligent Matching**: Hybrid LLM + rule-based compatibility scoring
- **Safety First**: Profile verification, blocking, and reporting capabilities
- **Product Experiments**: Built-in A/B testing framework for AI workflows
- **Metrics Dashboard**: Track match quality, engagement, and system performance

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL/SQLite
- **Frontend**: Streamlit
- **LLM**: OpenAI GPT-4 / Anthropic Claude
- **Testing**: pytest
- **Type Safety**: Full type hints with mypy

## Prerequisites

- Python 3.11+
- PostgreSQL (optional, SQLite works for dev)
- OpenAI API key or Anthropic API key

## Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo>
cd wanderwing
```

### 2. Install Dependencies

```bash
# Using poetry (recommended)
pip install poetry
poetry install

# Or using pip
pip install -e ".[dev]"
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 4. Initialize Database

```bash
make db-init
```

### 5. Run the Application

```bash
# Terminal 1: Start API server
make api

# Terminal 2: Start Streamlit frontend
make frontend
```

The API will be available at `http://localhost:8000`
The frontend will be available at `http://localhost:8501`

## Development

### Run Tests

```bash
# All tests
make test

# Unit tests only
make test-unit

# Integration tests only
make test-integration

# With coverage
make test-cov
```

### Code Quality

```bash
# Format code
make format

# Lint
make lint

# Type check
make typecheck

# Run all checks
make check
```

### Database Migrations

```bash
# Create a new migration
make db-migrate message="description"

# Apply migrations
make db-upgrade

# Rollback
make db-downgrade
```

## Project Structure

```
wanderwing/
├── src/wanderwing/
│   ├── agents/          # LLM agent workflows
│   ├── api/             # FastAPI routes and endpoints
│   ├── core/            # Business logic (matching, safety, experiments)
│   ├── db/              # Database models and repositories
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Orchestration layer
│   ├── llm/             # LLM client abstraction
│   ├── utils/           # Shared utilities
│   └── frontend/        # Streamlit application
├── tests/               # Test suite
├── scripts/             # Utility scripts
└── data/                # Local data files
```

## Key Workflows

### 1. Trip Creation Flow

```
User Input (natural language)
  → Itinerary Extraction Agent
  → Validation
  → Preference Enrichment
  → Structured Trip Object
```

### 2. Matching Flow

```
New Trip
  → Rule-based Filtering (destination, dates)
  → LLM Similarity Scoring
  → Hybrid Score Calculation
  → Match Recommendations
```

## Configuration

Key environment variables in `.env`:

- `DATABASE_URL`: Database connection string
- `OPENAI_API_KEY`: OpenAI API key (optional)
- `ANTHROPIC_API_KEY`: Anthropic API key (optional)
- `LLM_PROVIDER`: `openai` or `anthropic` (default: `openai`)
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `ENABLE_EXPERIMENTS`: Enable A/B testing (default: `true`)

## API Documentation

Once the API is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Contributing

1. Create a feature branch
2. Make your changes with tests
3. Run `make check` to ensure quality
4. Submit a PR

## License

MIT
