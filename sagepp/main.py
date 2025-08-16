"""
SAGE++ Trading Bot Main Entry Point

Orchestrates the complete trading system including:
- Multi-asset data pipeline
- Advanced range discovery  
- Temporal regime detection
- Intelligent grid construction
- Risk management
- Order execution
- Meta-learning optimization
"""

import asyncio
import argparse
import logging
import signal
import sys
from typing import Optional

# Will create these modules next
from sagepp.core.config import Config
from sagepp.core.logger import setup_logging, get_trading_logger
from sagepp.core.engine import TradingEngine

logger = get_trading_logger(__name__)


class SAGEPlusPlusBot:
    """Main trading bot controller"""
    
    def __init__(self, config_path: str = None, paper_trading: bool = True):
        self.config_path = config_path
        self.paper_trading = paper_trading
        self.engine: Optional[TradingEngine] = None
        self.running = False
        
    async def initialize(self):
        """Initialize all subsystems"""
        logger.info("Initializing SAGE++ Trading Bot...")
        
        # Load configuration
        self.config = Config.load(self.config_path)
        
        # Initialize trading engine
        self.engine = TradingEngine(self.config, paper_trading=self.paper_trading)
        await self.engine.initialize()
        
        logger.info("SAGE++ initialization complete")
        
    async def start(self):
        """Start the trading bot"""
        if not self.engine:
            await self.initialize()
            
        logger.info("Starting SAGE++ Trading Bot...")
        self.running = True
        
        try:
            # Start all subsystems
            await self.engine.start()
            
            # Main event loop
            while self.running:
                await asyncio.sleep(1)
                # Monitor system health, handle events
                
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            await self.shutdown()
            
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down SAGE++ Trading Bot...")
        self.running = False
        
        if self.engine:
            await self.engine.shutdown()
            
        logger.info("SAGE++ shutdown complete")
        
    def handle_signal(self, sig, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {sig}, initiating shutdown...")
        self.running = False


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="SAGE++ Trading Bot - Advanced Grid Trading System"
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='config/default.yaml',
        help='Configuration file path'
    )
    
    parser.add_argument(
        '--paper',
        action='store_true',
        help='Run in paper trading mode (default: True)'
    )
    
    parser.add_argument(
        '--live',
        action='store_true',
        help='Run in live trading mode (DANGER: Real money!)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    
    return parser.parse_args()


async def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Basic logging setup (will enhance with proper logger module)
    setup_logging(
        log_level=args.log_level,
        log_file='logs/sagepp.log',
        enable_console=True,
        enable_json=True
    )
    
    # Determine trading mode
    paper_trading = not args.live
    if args.live:
        logger.warning("LIVE TRADING MODE ENABLED - REAL MONEY AT RISK!")
        confirm = input("Are you sure you want to trade with real money? (yes/no): ")
        if confirm.lower() != 'yes':
            logger.info("Exiting - user cancelled live trading")
            return
    else:
        logger.info("Running in PAPER TRADING mode")
    
    # Create and start bot
    bot = SAGEPlusPlusBot(
        config_path=args.config,
        paper_trading=paper_trading
    )
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, bot.handle_signal)
    signal.signal(signal.SIGTERM, bot.handle_signal)
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt, shutting down...")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        raise
    finally:
        await bot.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
