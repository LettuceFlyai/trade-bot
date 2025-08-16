<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# SAGE++ Trading Bot Development Instructions

This workspace contains the SAGE++ (Stochastic Adaptive Grid Engine Plus Plus) Trading Bot - an advanced algorithmic trading system implementing doctoral-level quantitative strategies with temporal advantage systems for predictive grid trading on Binance Spot.

## Project Status: ✅ COMPLETE INITIAL SETUP

- [x] **Verified copilot-instructions.md created**
- [x] **Clarified Project Requirements** - SAGE++ Trading Bot with Python 3.10+, asyncio, ML/quant libraries, multi-exchange support
- [x] **Scaffolded the Project** - Project structure created with all core modules, config, requirements
- [x] **Customized the Project** - All major subsystem modules created and integrated
- [x] **No Extensions Required** - No extensions specified by get_project_setup_info
- [x] **Compiled Successfully** - Virtual environment created, dependencies installed, imports verified
- [x] **Created and Run Task** - Task created for SAGE++ Paper Trading and successfully executed
- [x] **Launched the Project** - Successfully launched SAGE++ in paper trading mode
- [x] **Documentation Complete** - README.md and copilot-instructions.md exist with current project info

## Architecture Overview

The SAGE++ system is organized into modular subsystems:

- **`sagepp/core/`** - Core infrastructure (config, logging, main engine)
- **`sagepp/discovery/`** - Range discovery & regime detection (KDE, HMM, time crystals)  
- **`sagepp/grid/`** - Grid construction & position sizing (entropy-weighted, Kelly criterion)
- **`sagepp/temporal/`** - Temporal advantage systems (correlation, whale detection, sentiment)
- **`sagepp/risk/`** - Multi-layer risk management (circuit breakers, stops)
- **`sagepp/execution/`** - Smart order management (anti-detection, latency optimization)
- **`sagepp/meta/`** - Meta-learning & self-optimization
- **`sagepp/monitoring/`** - Logging, alerts, dashboard
- **`sagepp/utils/`** - Shared utilities

## Development Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints for all function parameters and return values
- Include comprehensive docstrings with Args/Returns sections
- Implement proper error handling with structured logging

### Trading System Principles
- **Safety First**: Paper trading by default, multiple confirmation layers for live trading
- **Risk Management**: Multi-layer protection with circuit breakers and position limits
- **Performance**: Sub-100ms order placement, efficient async operations
- **Observability**: Comprehensive logging and monitoring for all system components

### Key Features to Implement

1. **Multi-Asset Data Pipeline** - Real-time monitoring with WebSocket and REST API integration
2. **Advanced Range Discovery** - KDE with whale behavior prediction and volume profile analysis
3. **Temporal Regime Detection** - HMM with deterministic time crystal patterns
4. **Intelligent Grid Construction** - Entropy-weighted spacing with market maker exploitation
5. **Dynamic Position Sizing** - Modified Kelly Criterion with multi-factor adjustment
6. **Temporal Advantage Systems** - Cross-asset correlation, whale shadow detection, sentiment velocity
7. **Meta-Learning Engine** - Continuous self-improvement and pattern discovery

### Configuration Management
- Environment variables for sensitive data (API keys, passwords)
- YAML configuration files for system parameters
- Multiple environment support (paper/live trading modes)

### Testing Strategy
- Unit tests for individual components
- Integration tests for subsystem interactions
- Paper trading validation before live deployment
- Performance benchmarking and monitoring

### Deployment Approach
- Phased rollout starting with paper trading
- Gradual capital allocation increases based on performance
- Multi-region failover capability on AWS/GCP
- Comprehensive monitoring and alerting

## Quick Commands

```bash
# Run in paper trading mode (default)
python -m sagepp.main --paper --config config/default.yaml

# Run with debug logging
python -m sagepp.main --paper --log-level DEBUG

# View help
python -m sagepp.main --help
```

## Next Development Priorities

1. **Complete Data Manager** - Implement Binance connectivity with ccxt-pro
2. **Range Discovery** - Finish whale detection and time crystal patterns
3. **Risk Management** - Implement comprehensive risk framework
4. **Order Execution** - Build smart order management with anti-detection
5. **Meta-Learning** - Add performance tracking and strategy optimization

---

*The system is designed to be antifragile - getting stronger from market volatility through continuous learning and adaptation.*
