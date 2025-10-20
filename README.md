# Trading Data Adapter (Python)

**Component Type**: Data Adapter
**Language**: Python 3.13+
**Architecture**: Clean Architecture
**Status**: Foundation Phase

---

## Overview

Data persistence adapter for the Trading System Engine. Provides domain-specific APIs for strategy management, portfolio tracking, and performance analytics following Clean Architecture patterns.

**Purpose**:
- Abstract PostgreSQL database operations for trading domain
- Provide repository interfaces for trading entities
- Handle data persistence for trading strategies, orders, and positions
- Support multi-instance deployments with isolated schemas

---

## Features

- **Clean Architecture**: Domain-driven design with clear layer separation
- **Repository Pattern**: Interface-based data access
- **Multi-Instance Support**: Schema-based isolation (e.g., `trading_algo1`, `trading_algo2`)
- **Configuration Derivation**: Auto-derives database schema from instance name
- **Health Monitoring**: Health endpoints with instance metadata
- **Observability**: Prometheus metrics with RED pattern (Rate, Errors, Duration)

---

## Project Structure

```
trading-data-adapter-py/
├── src/trading_data_adapter/
│   ├── domain/              # Domain models and interfaces
│   ├── infrastructure/      # PostgreSQL implementations
│   └── config.py           # Configuration with instance derivation
├── tests/
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests with PostgreSQL
├── docs/
│   └── prs/               # Pull request documentation
└── .claude/
    └── plugins/           # Workflow automation plugins
```

---

## Quick Start

### Prerequisites

- Python 3.13+
- PostgreSQL 15+
- Redis 7+ (for service discovery)
- Conda environment: `py313_trading_ecosystem_dev`

### Installation

```bash
# Activate conda environment
conda activate py313_trading_ecosystem_dev

# Install dependencies (when available)
pip install -e .

# Run tests
pytest tests/ -v
```

### Configuration

Configuration is derived from the instance name:

```python
# Instance name: "algo-trader-1"
# Derives to:
# - PostgreSQL schema: "trading_algo_trader_1"
# - Redis namespace: "trading:algo-trader-1"
```

**Environment Variables**:
- `INSTANCE_NAME` - Instance identifier (e.g., "algo-trader-1")
- `POSTGRES_HOST` - PostgreSQL host
- `POSTGRES_PORT` - PostgreSQL port (default: 5432)
- `REDIS_HOST` - Redis host
- `REDIS_PORT` - Redis port (default: 6379)

---

## Development

### Running Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests (requires PostgreSQL)
pytest tests/integration/ -v

# With coverage
pytest tests/ -v --cov=src/trading_data_adapter --cov-report=term-missing
```

### Code Quality

```bash
# Linting
ruff check src/ tests/

# Type checking
mypy src/

# Formatting
ruff format src/ tests/
```

---

## Architecture

### Clean Architecture Layers

1. **Domain Layer** (`src/trading_data_adapter/domain/`)
   - Entities: Strategy, Order, Trade, Position
   - Repository Interfaces: Pure Python protocols
   - No external dependencies

2. **Infrastructure Layer** (`src/trading_data_adapter/infrastructure/`)
   - PostgreSQL repository implementations
   - Database connection management
   - Schema creation and migrations

3. **Configuration** (`src/trading_data_adapter/config.py`)
   - Instance-based configuration derivation
   - Environment variable management
   - Multi-instance support

### Multi-Instance Design

Supports multiple trading system instances with isolated data:

```
PostgreSQL Schemas:
├── trading_algo_trader_1/     # Instance 1 data
├── trading_algo_trader_2/     # Instance 2 data
└── trading_backtest_1/        # Backtest instance

Redis Namespaces:
├── trading:algo-trader-1      # Instance 1 cache
├── trading:algo-trader-2      # Instance 2 cache
└── trading:backtest-1         # Backtest cache
```

---

## Integration

### Used By
- **trading-system-engine-py**: Consumes this adapter for data persistence

### Dependencies
- **PostgreSQL**: `trading` database with instance-specific schemas
- **Redis**: Service discovery and caching
- **protobuf-schemas**: gRPC service definitions (future)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow, code standards, and pull request guidelines.

---

## Epic Context

**Epic**: TSE-0003 - Trading Data Adapter Foundation
**Milestone**: Repository Infrastructure Setup
**Project**: Trading Ecosystem Simulation

See [TODO.md](TODO.md) for current tasks and [project-plan](../project-plan/) for overall project context.

---

## License

Internal project - Trading Ecosystem Simulation

---

## Related Repositories

- **Project Plan**: `../project-plan/`
- **Trading System Engine**: `../trading-system-engine-py/`
- **Orchestrator**: `../orchestrator-docker/`
- **Protocol Buffers**: `../protobuf-schemas/`

---

**Status**: Foundation phase - Repository infrastructure complete
**Last Updated**: 2025-10-20
