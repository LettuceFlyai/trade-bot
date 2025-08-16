"""
Configuration Management for SAGE++ Trading Bot

Handles loading, validation, and management of all system configuration
including trading parameters, API keys, risk limits, and system settings.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class TradingConfig:
    """Trading configuration parameters"""
    primary_pair: str = "SOL/USDT"
    initial_capital: float = 10000.0
    
    # Capital allocation
    grid_allocation: float = 0.85
    reserve_allocation: float = 0.10
    testing_allocation: float = 0.05
    
    # Grid parameters
    base_levels: int = 40
    min_spacing_pct: float = 0.0015  # 0.15%
    max_spacing_pct: float = 0.01    # 1.0%
    min_profit_per_grid: float = 0.003
    
    # Fee optimization
    use_bnb_discount: bool = True
    maker_only: bool = True
    target_fee_rate: float = 0.00075  # 0.075%


@dataclass
class ExchangeConfig:
    """Exchange connectivity configuration"""
    name: str = "binance"
    
    # API Configuration
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    
    # Rate limits
    max_requests_per_minute: int = 1200
    max_orders_per_minute: int = 100
    
    # Connection settings
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    
    # Security
    ip_whitelist_only: bool = True
    testnet: bool = True


@dataclass
class RiskConfig:
    """Risk management configuration"""
    # Position limits
    max_grid_exposure_pct: float = 0.40  # 40% of capital
    max_single_level_pct: float = 0.02   # 2% per level
    max_directional_bias_pct: float = 0.60  # 60% long or short
    max_correlated_exposure_pct: float = 0.60
    
    # Stop loss levels
    soft_stop_trigger_pct: float = 0.05   # 5% outside range
    medium_stop_trigger_pct: float = 0.10  # 10% outside range
    hard_stop_trigger_pct: float = 0.15   # 15% outside range
    emergency_stop_drawdown_pct: float = 0.20  # 20% drawdown
    
    # Circuit breakers
    max_consecutive_losses: int = 5
    max_api_errors: int = 10
    max_slippage_pct: float = 0.005  # 0.5%
    
    # Inventory management
    target_base_pct: float = 0.50
    target_quote_pct: float = 0.50
    rebalance_trigger_pct: float = 0.70  # Rebalance at 70/30
    rebalance_frequency_hours: int = 6


@dataclass
class DatabaseConfig:
    """Database configuration"""
    # PostgreSQL/TimescaleDB
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "sagepp"
    postgres_user: str = "sagepp"
    postgres_password: Optional[str] = None
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # S3 Backup
    s3_bucket: Optional[str] = None
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None
    s3_region: str = "us-east-1"


@dataclass
class MonitoringConfig:
    """Monitoring and alerting configuration"""
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/sagepp.log"
    log_max_bytes: int = 10_000_000  # 10MB
    log_backup_count: int = 5
    
    # Telegram alerts
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    # Email alerts
    email_smtp_host: Optional[str] = None
    email_smtp_port: int = 587
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    email_to: Optional[str] = None
    
    # Metrics
    enable_prometheus: bool = True
    prometheus_port: int = 8000


@dataclass
class Config:
    """Main configuration class"""
    trading: TradingConfig = field(default_factory=TradingConfig)
    exchange: ExchangeConfig = field(default_factory=ExchangeConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # System settings
    paper_trading: bool = True
    debug_mode: bool = False
    config_file: Optional[str] = None
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'Config':
        """Load configuration from file and environment variables"""
        config = cls()
        
        if config_path and os.path.exists(config_path):
            config.config_file = config_path
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)
                config._update_from_dict(data)
        
        # Override with environment variables
        config._load_from_env()
        
        # Validate configuration
        config._validate()
        
        logger.info(f"Configuration loaded from {config_path or 'defaults'}")
        return config
    
    def _update_from_dict(self, data: Dict[str, Any]):
        """Update configuration from dictionary"""
        if 'trading' in data:
            for key, value in data['trading'].items():
                if hasattr(self.trading, key):
                    setattr(self.trading, key, value)
        
        if 'exchange' in data:
            for key, value in data['exchange'].items():
                if hasattr(self.exchange, key):
                    setattr(self.exchange, key, value)
        
        if 'risk' in data:
            for key, value in data['risk'].items():
                if hasattr(self.risk, key):
                    setattr(self.risk, key, value)
        
        if 'database' in data:
            for key, value in data['database'].items():
                if hasattr(self.database, key):
                    setattr(self.database, key, value)
        
        if 'monitoring' in data:
            for key, value in data['monitoring'].items():
                if hasattr(self.monitoring, key):
                    setattr(self.monitoring, key, value)
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        # Exchange API keys (sensitive)
        self.exchange.api_key = os.getenv('BINANCE_API_KEY')
        self.exchange.api_secret = os.getenv('BINANCE_API_SECRET')
        
        # Testnet configuration
        if os.getenv('BINANCE_TESTNET', '').lower() in ('true', '1', 'yes'):
            self.exchange.testnet = True
        if os.getenv('BINANCE_SANDBOX', '').lower() in ('true', '1', 'yes'):
            self.exchange.testnet = True  # Sandbox mode uses testnet
        
        # Database credentials
        self.database.postgres_password = os.getenv('POSTGRES_PASSWORD')
        self.database.redis_password = os.getenv('REDIS_PASSWORD')
        
        # S3 credentials
        self.database.s3_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.database.s3_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        # Telegram
        self.monitoring.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.monitoring.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        # Email
        self.monitoring.email_username = os.getenv('EMAIL_USERNAME')
        self.monitoring.email_password = os.getenv('EMAIL_PASSWORD')
        
        # Trading mode
        if os.getenv('PAPER_TRADING', '').lower() in ('false', '0', 'no'):
            self.paper_trading = False
        
        # Special case: if testnet is enabled, we can safely turn off paper trading
        if self.exchange.testnet and os.getenv('TESTNET_TRADING', '').lower() in ('true', '1', 'yes'):
            self.paper_trading = False  # Testnet uses real API but fake money
        
        # Debug mode
        if os.getenv('DEBUG_MODE', '').lower() in ('true', '1', 'yes'):
            self.debug_mode = True
    
    def _validate(self):
        """Validate configuration"""
        errors = []
        
        # Check required API keys for live trading and testnet
        if not self.paper_trading:
            if not self.exchange.api_key:
                trading_mode = "testnet" if self.exchange.testnet else "live"
                errors.append(f"BINANCE_API_KEY required for {trading_mode} trading")
            if not self.exchange.api_secret:
                trading_mode = "testnet" if self.exchange.testnet else "live"
                errors.append(f"BINANCE_API_SECRET required for {trading_mode} trading")
        
        # Validate trading parameters
        if self.trading.initial_capital <= 0:
            errors.append("initial_capital must be positive")
        
        if (self.trading.grid_allocation + 
            self.trading.reserve_allocation + 
            self.trading.testing_allocation) != 1.0:
            errors.append("Capital allocations must sum to 1.0")
        
        # Validate risk limits
        if self.risk.max_grid_exposure_pct > 1.0:
            errors.append("max_grid_exposure_pct cannot exceed 100%")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
        
        # Log trading mode
        if self.paper_trading:
            logger.info("🟢 Running in PAPER TRADING mode (simulated)")
        elif self.exchange.testnet:
            logger.info("🟡 Running in TESTNET mode (real API, fake money)")
        else:
            logger.warning("🔴 Running in LIVE TRADING mode (REAL MONEY!)")
    
    def save(self, config_path: str):
        """Save configuration to file"""
        config_dict = {
            'trading': {
                'primary_pair': self.trading.primary_pair,
                'initial_capital': self.trading.initial_capital,
                'grid_allocation': self.trading.grid_allocation,
                'reserve_allocation': self.trading.reserve_allocation,
                'testing_allocation': self.trading.testing_allocation,
                'base_levels': self.trading.base_levels,
                'min_spacing_pct': self.trading.min_spacing_pct,
                'max_spacing_pct': self.trading.max_spacing_pct,
                'min_profit_per_grid': self.trading.min_profit_per_grid,
                'use_bnb_discount': self.trading.use_bnb_discount,
                'maker_only': self.trading.maker_only,
                'target_fee_rate': self.trading.target_fee_rate,
            },
            'exchange': {
                'name': self.exchange.name,
                'max_requests_per_minute': self.exchange.max_requests_per_minute,
                'max_orders_per_minute': self.exchange.max_orders_per_minute,
                'timeout': self.exchange.timeout,
                'retry_attempts': self.exchange.retry_attempts,
                'retry_delay': self.exchange.retry_delay,
                'ip_whitelist_only': self.exchange.ip_whitelist_only,
                'testnet': self.exchange.testnet,
            },
            'risk': {
                'max_grid_exposure_pct': self.risk.max_grid_exposure_pct,
                'max_single_level_pct': self.risk.max_single_level_pct,
                'max_directional_bias_pct': self.risk.max_directional_bias_pct,
                'max_correlated_exposure_pct': self.risk.max_correlated_exposure_pct,
                'soft_stop_trigger_pct': self.risk.soft_stop_trigger_pct,
                'medium_stop_trigger_pct': self.risk.medium_stop_trigger_pct,
                'hard_stop_trigger_pct': self.risk.hard_stop_trigger_pct,
                'emergency_stop_drawdown_pct': self.risk.emergency_stop_drawdown_pct,
                'max_consecutive_losses': self.risk.max_consecutive_losses,
                'max_api_errors': self.risk.max_api_errors,
                'max_slippage_pct': self.risk.max_slippage_pct,
                'target_base_pct': self.risk.target_base_pct,
                'target_quote_pct': self.risk.target_quote_pct,
                'rebalance_trigger_pct': self.risk.rebalance_trigger_pct,
                'rebalance_frequency_hours': self.risk.rebalance_frequency_hours,
            },
            'monitoring': {
                'log_level': self.monitoring.log_level,
                'log_file': self.monitoring.log_file,
                'log_max_bytes': self.monitoring.log_max_bytes,
                'log_backup_count': self.monitoring.log_backup_count,
                'enable_prometheus': self.monitoring.enable_prometheus,
                'prometheus_port': self.monitoring.prometheus_port,
            }
        }
        
        # Create directory if it doesn't exist
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        
        logger.info(f"Configuration saved to {config_path}")


# Default configuration singleton
default_config = Config()
