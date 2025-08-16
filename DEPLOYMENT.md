# SAGE++ Trading Bot - DevOps Deployment Checklist

## Pre-Deployment Validation ✅

### 1. Environment Setup
- [x] Python 3.13+ installed and virtual environment active
- [x] All required dependencies installed (`pip install -r requirements.txt`)
- [x] All optional trading dependencies available (ccxt, sklearn, redis, etc.)
- [x] Directory structure complete with all __init__.py files
- [x] Configuration files present (default.yaml, .env.example)
- [x] Log directory writable

### 2. Code Quality
- [x] No syntax errors in core modules
- [x] All imports resolve successfully 
- [x] Configuration validation working
- [x] Logging system functional
- [x] Health check passes (run `python health_check.py`)

### 3. Security
- [x] .env file not committed to repository
- [x] .gitignore properly configured (excludes .env, logs, cache)
- [x] API keys handled via environment variables only
- [x] Paper trading enabled by default
- [x] Live trading requires explicit confirmation

## Deployment Environments

### Paper Trading (Safe - Default)
```bash
# Configuration
PAPER_TRADING=true

# Run command
python -m sagepp.main --paper --config config/default.yaml
```

### Live Trading (DANGER - Real Money!)
```bash
# Required environment variables
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
PAPER_TRADING=false

# Run command (requires confirmation)
python -m sagepp.main --live --config config/default.yaml
```

## Monitoring Setup

### Log Files
- `logs/sagepp.log` - Standard log output
- `logs/sagepp.json` - Structured JSON logs
- Log rotation enabled (10MB files, 5 backups)

### Health Monitoring
```bash
# Run health check
python health_check.py

# Check system status
python -c "from sagepp.core.engine import TradingEngine; print('Engine OK')"
```

## Common Issues & Solutions

### Issue: Import Errors
**Solution**: Ensure virtual environment is active and all dependencies installed
```bash
pip install -r requirements.txt
```

### Issue: Configuration Not Found
**Solution**: Verify config file path and YAML syntax
```bash
python -c "import yaml; yaml.safe_load(open('config/default.yaml'))"
```

### Issue: Log Directory Permissions
**Solution**: Ensure logs/ directory is writable
```bash
touch logs/test.log && rm logs/test.log
```

### Issue: API Connection Errors (Live Trading)
**Solution**: Verify API keys and network connectivity
- Check API key permissions on Binance
- Verify IP whitelist settings
- Test network connectivity to api.binance.com

## Performance Baselines

### Startup Time
- Expected: < 5 seconds in paper trading mode
- Target: < 2 seconds for component initialization

### Memory Usage
- Initial: ~50-100MB 
- Runtime: ~100-200MB (depends on data retention)

### CPU Usage
- Idle: < 5%
- Active trading: 10-30%

## Scaling Considerations

### Single Instance Limits
- Max orders per minute: 100 (exchange limit)
- Max concurrent requests: 10
- Recommended capital: $1,000 - $50,000

### Multi-Instance Deployment
- Use different trading pairs per instance
- Implement coordination layer for shared resources
- Monitor aggregate exposure across instances

## Backup Strategy

### Configuration Backup
- Backup config/ directory regularly
- Version control all configuration changes
- Keep environment variable documentation updated

### State Backup
- Trading history stored in PostgreSQL
- Redis state snapshots every 5 minutes  
- S3 backup every 6 hours

### Recovery Procedures
1. Restore configuration from backup
2. Restart with paper trading mode
3. Verify system health
4. Resume live trading if validated

## Maintenance Schedule

### Daily
- [ ] Check log files for errors
- [ ] Verify system health metrics
- [ ] Monitor performance metrics

### Weekly  
- [ ] Review trading performance
- [ ] Update dependencies if needed
- [ ] Backup configuration and logs

### Monthly
- [ ] Full system audit
- [ ] Performance optimization review  
- [ ] Security assessment
- [ ] Documentation updates

---

**🚨 CRITICAL SAFETY REMINDER 🚨**

**ALWAYS start with paper trading mode for:**
- New deployments
- Configuration changes  
- Code updates
- System testing

**NEVER deploy directly to live trading without:**
- Successful paper trading validation
- Health check passing
- Performance baseline verification
- Risk limits configured
- Emergency stop procedures tested
