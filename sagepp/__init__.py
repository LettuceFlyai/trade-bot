"""
SAGE++ Trading Bot - Stochastic Adaptive Grid Engine Plus Plus

Advanced algorithmic trading system implementing doctoral-level quantitative strategies
with temporal advantage systems for predictive grid trading on Binance Spot.
"""

__version__ = "3.0.0"
__author__ = "LettuceFlyai"
__description__ = "Advanced Grid Trading Bot with Temporal Advantage Systems"

# Core imports for easy access
from sagepp.core.config import Config
from sagepp.core.logger import setup_logging

__all__ = [
    "Config",
    "setup_logging",
]
