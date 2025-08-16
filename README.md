# SAGE++ Trading Bot

Stochastic Adaptive Grid Engine Plus Plus (SAGE++) for Binance Spot trading. Implements doctoral-level quantitative strategies with temporal advantage systems for predictive grid trading.

## Overview

SAGE++ is an advanced algorithmic trading system that combines:

- **Multi-Asset Data Pipeline**: Real-time monitoring of primary and correlated assets
- **Advanced Range Discovery**: Kernel Density Estimation with whale behavior prediction  
- **Temporal Regime Detection**: Hidden Markov Models with deterministic time crystal patterns
- **Intelligent Grid Construction**: Entropy-weighted spacing with market maker exploitation
- **Dynamic Position Sizing**: Modified Kelly Criterion with multi-factor adjustment
- **Temporal Advantage Systems**: Cross-asset correlation, whale shadow detection, sentiment velocity
- **Multi-Layer Risk Management**: Defense-in-depth with circuit breakers
- **Smart Order Execution**: Anti-detection with latency optimization
- **Meta-Learning Engine**: Continuous self-improvement and pattern discovery

## Features

- **Multi-temporal operation**: Exploits opportunities across 5 time horizons (30s to 4h)
- **Predictive architecture**: Anticipates moves rather than reacting
- **Self-improving intelligence**: Meta-learning increases edge over time
- **Risk-layered design**: Multiple fail-safes prevent catastrophic losses
- **Market adaptive**: Automatically adjusts to changing conditions
- **Microstructure exploitation**: Takes advantage of market maker weaknesses

## Technology Stack

- **Core**: Python 3.10+, asyncio/aiohttp
- **Numerical**: NumPy, Pandas, SciPy  
- **ML/Statistics**: scikit-learn, hmmlearn, arch
- **Exchange**: ccxt-pro
- **Data Storage**: PostgreSQL (TimescaleDB), Redis, S3
- **Monitoring**: DataDog/New Relic, ELK Stack, Prometheus, Grafana
- **Infrastructure**: AWS/GCP with multi-region failover

## Performance Targets

| Market Condition | Daily Return | Max Drawdown | Sharpe Ratio | Win Rate |
|-----------------|--------------|--------------|--------------|----------|
| Optimal (Ranging) | 0.5-1.0% | 5% | >3.0 | 80-85% |
| Normal | 0.3-0.5% | 10% | 2.0-3.0 | 70-80% |
| Challenging | 0.1-0.3% | 15% | 1.5-2.0 | 65-70% |
| Adverse (Trending) | 0.0-0.1% | 20% | <1.5 | 60-65% |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run in paper trading mode
python -m sagepp.main --paper

# Run live trading (after validation)
python -m sagepp.main --live
```

## Project Structure

```text
sagepp/
├── core/               # Core infrastructure & data pipeline
├── discovery/          # Range discovery & regime detection  
├── grid/              # Grid construction & position sizing
├── temporal/          # Temporal advantage systems
├── risk/              # Risk management framework
├── execution/         # Order execution intelligence
├── meta/              # Meta-learning & optimization
├── monitoring/        # Logging, alerts, dashboard
├── config/            # Configuration management
└── utils/             # Shared utilities
```

## Security & Risk

- **API Security**: Environment variables, secrets management, IP whitelist
- **Position Limits**: Max 40% grid exposure, 2% per level
- **Stop Loss Hierarchy**: 4-level system (soft → emergency)
- **Circuit Breakers**: Rate limiting, consecutive loss protection
- **Black Swan Protection**: Flash crash detection, exchange outage handling

## Documentation

- See `docs/` for detailed implementation guides
- See `.github/copilot-instructions.md` for development checklist
- See individual module README files for component details

## License

Proprietary - All rights reserved
