"""
Advanced Range Discovery System for SAGE++

Implements Kernel Density Estimation with Predictive Enhancement
combining statistical range finding with whale behavior prediction.

Based on Section 2.1 of the SAGE++ specification.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from scipy import stats
from sklearn.neighbors import KernelDensity

from sagepp.core.config import Config
from sagepp.core.logger import get_trading_logger

logger = get_trading_logger(__name__)


class KernelDensityEstimator:
    """
    Kernel Density Estimation for price range discovery
    Uses Scott's Rule with adaptive adjustment for bandwidth selection
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.bandwidth_method = 'scott'  # Scott's Rule with adaptive adjustment
        self.kernel_type = 'gaussian'
        self.evaluation_points = 1000
        self.probability_mass_threshold = 0.90
        
    def estimate_range(self, price_data: np.ndarray) -> Dict[str, float]:
        """
        Estimate optimal trading range using KDE
        
        Args:
            price_data: Array of historical prices
            
        Returns:
            Dict containing range boundaries and confidence metrics
        """
        try:
            if len(price_data) < 50:
                logger.warning("Insufficient price data for KDE, using simple range")
                return self._simple_range_fallback(price_data)
            
            # Prepare data
            log_returns = np.diff(np.log(price_data))
            log_returns = log_returns[~np.isnan(log_returns)]
            
            if len(log_returns) < 30:
                return self._simple_range_fallback(price_data)
            
            # Calculate bandwidth using Scott's rule with adaptive adjustment
            bandwidth = self._calculate_adaptive_bandwidth(log_returns)
            
            # Fit KDE
            kde = KernelDensity(
                kernel=self.kernel_type,
                bandwidth=bandwidth
            )
            kde.fit(log_returns.reshape(-1, 1))
            
            # Evaluate density
            log_return_range = np.linspace(
                log_returns.min(), log_returns.max(), self.evaluation_points
            )
            log_density = kde.score_samples(log_return_range.reshape(-1, 1))
            density = np.exp(log_density)
            
            # Find range containing specified probability mass
            range_bounds = self._find_probability_range(
                log_return_range, density, self.probability_mass_threshold
            )
            
            # Convert back to price space
            current_price = price_data[-1]
            lower_bound = current_price * np.exp(range_bounds['lower'])
            upper_bound = current_price * np.exp(range_bounds['upper'])
            
            result = {
                'lower': lower_bound,
                'upper': upper_bound,
                'center': current_price,
                'range_pct': (upper_bound - lower_bound) / current_price,
                'confidence': range_bounds['confidence'],
                'method': 'kde'
            }
            
            logger.info(
                f"KDE range estimated: {lower_bound:.4f} - {upper_bound:.4f} "
                f"({result['range_pct']:.2%} width, {result['confidence']:.2%} confidence)"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in KDE range estimation: {e}")
            return self._simple_range_fallback(price_data)
    
    def _calculate_adaptive_bandwidth(self, data: np.ndarray) -> float:
        """Calculate bandwidth using Scott's rule with adaptive adjustment"""
        n = len(data)
        std_dev = np.std(data)
        
        # Scott's rule
        scott_bandwidth = 1.06 * std_dev * (n ** (-1/5))
        
        # Adaptive adjustment based on data characteristics
        volatility = np.std(data)
        if volatility > 0.02:  # High volatility
            adaptive_factor = 1.2  # Slightly wider bandwidth
        elif volatility < 0.005:  # Low volatility
            adaptive_factor = 0.8  # Slightly narrower bandwidth
        else:
            adaptive_factor = 1.0
        
        return scott_bandwidth * adaptive_factor
    
    def _find_probability_range(
        self, x_values: np.ndarray, density: np.ndarray, target_mass: float
    ) -> Dict[str, float]:
        """Find range containing target probability mass"""
        # Normalize density to probability
        total_area = np.trapz(density, x_values)
        probability = density / total_area
        
        # Find range containing target mass
        cumulative = np.cumsum(probability)
        cumulative = cumulative / cumulative[-1]  # Normalize
        
        # Find symmetric range around mode
        mode_idx = np.argmax(density)
        
        # Expand symmetrically until we capture target mass
        left_idx = mode_idx
        right_idx = mode_idx
        
        while (right_idx < len(cumulative) - 1 and left_idx > 0):
            current_mass = cumulative[right_idx] - cumulative[left_idx]
            if current_mass >= target_mass:
                break
            
            # Expand the side with lower density first
            if left_idx > 0 and (right_idx >= len(cumulative) - 1 or 
                                density[left_idx-1] > density[right_idx+1]):
                left_idx -= 1
            elif right_idx < len(cumulative) - 1:
                right_idx += 1
            else:
                left_idx -= 1
        
        final_mass = cumulative[right_idx] - cumulative[left_idx]
        
        return {
            'lower': x_values[left_idx],
            'upper': x_values[right_idx],
            'confidence': final_mass
        }
    
    def _simple_range_fallback(self, price_data: np.ndarray) -> Dict[str, float]:
        """Simple range calculation fallback"""
        if len(price_data) < 2:
            current_price = price_data[0] if len(price_data) > 0 else 100.0
            return {
                'lower': current_price * 0.95,
                'upper': current_price * 1.05,
                'center': current_price,
                'range_pct': 0.10,
                'confidence': 0.50,
                'method': 'simple_fallback'
            }
        
        current_price = price_data[-1]
        volatility = np.std(price_data) / np.mean(price_data)
        range_factor = min(max(volatility * 2, 0.02), 0.15)  # 2% to 15%
        
        return {
            'lower': current_price * (1 - range_factor),
            'upper': current_price * (1 + range_factor),
            'center': current_price,
            'range_pct': range_factor * 2,
            'confidence': 0.70,
            'method': 'simple'
        }


class VolumeProfileAnalyzer:
    """
    Volume Profile Analysis for high-volume node identification
    Identifies optimal grid placement based on volume concentration
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.lookback_days = 7
        self.bin_size_pct = 0.001  # 0.1% of price
        self.significance_threshold = 1.5  # 1.5x average volume
        
    def analyze_volume_profile(
        self, price_data: np.ndarray, volume_data: np.ndarray
    ) -> Dict[str, any]:
        """
        Analyze volume profile to identify high-volume nodes
        
        Args:
            price_data: Array of prices
            volume_data: Array of volumes
            
        Returns:
            Dict containing volume profile analysis
        """
        try:
            if len(price_data) != len(volume_data) or len(price_data) < 100:
                logger.warning("Insufficient data for volume profile analysis")
                return {'hvns': [], 'lvns': [], 'poc': None, 'value_area': None}
            
            # Create price bins
            price_min, price_max = price_data.min(), price_data.max()
            bin_size = (price_max - price_min) * self.bin_size_pct
            bins = np.arange(price_min, price_max + bin_size, bin_size)
            
            # Aggregate volume by price bins
            volume_profile = np.zeros(len(bins) - 1)
            for i, price in enumerate(price_data):
                bin_idx = np.searchsorted(bins, price) - 1
                if 0 <= bin_idx < len(volume_profile):
                    volume_profile[bin_idx] += volume_data[i]
            
            # Calculate bin centers
            bin_centers = (bins[:-1] + bins[1:]) / 2
            
            # Find Point of Control (highest volume)
            poc_idx = np.argmax(volume_profile)
            poc_price = bin_centers[poc_idx]
            
            # Find High Volume Nodes (HVNs)
            avg_volume = np.mean(volume_profile)
            hvn_threshold = avg_volume * self.significance_threshold
            hvn_indices = np.where(volume_profile > hvn_threshold)[0]
            hvns = bin_centers[hvn_indices].tolist()
            
            # Find Low Volume Nodes (LVNs) - gaps in volume
            lvn_threshold = avg_volume * 0.5
            lvn_indices = np.where(volume_profile < lvn_threshold)[0]
            lvns = bin_centers[lvn_indices].tolist()
            
            # Calculate Value Area (70% of volume)
            value_area = self._calculate_value_area(bin_centers, volume_profile, 0.70)
            
            result = {
                'hvns': hvns,
                'lvns': lvns,
                'poc': poc_price,
                'value_area': value_area,
                'volume_profile': {
                    'prices': bin_centers.tolist(),
                    'volumes': volume_profile.tolist()
                }
            }
            
            logger.info(
                f"Volume profile analyzed: POC={poc_price:.4f}, "
                f"HVNs={len(hvns)}, LVNs={len(lvns)}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in volume profile analysis: {e}")
            return {'hvns': [], 'lvns': [], 'poc': None, 'value_area': None}
    
    def _calculate_value_area(
        self, prices: np.ndarray, volumes: np.ndarray, target_pct: float
    ) -> Optional[Dict[str, float]]:
        """Calculate value area containing target percentage of volume"""
        try:
            total_volume = np.sum(volumes)
            target_volume = total_volume * target_pct
            
            # Start from POC and expand outward
            poc_idx = np.argmax(volumes)
            left_idx = poc_idx
            right_idx = poc_idx
            current_volume = volumes[poc_idx]
            
            while current_volume < target_volume:
                # Decide which direction to expand
                left_vol = volumes[left_idx - 1] if left_idx > 0 else 0
                right_vol = volumes[right_idx + 1] if right_idx < len(volumes) - 1 else 0
                
                if left_vol > right_vol and left_idx > 0:
                    left_idx -= 1
                    current_volume += volumes[left_idx]
                elif right_idx < len(volumes) - 1:
                    right_idx += 1
                    current_volume += volumes[right_idx]
                else:
                    break
            
            return {
                'lower': prices[left_idx],
                'upper': prices[right_idx],
                'volume_pct': current_volume / total_volume
            }
            
        except Exception as e:
            logger.error(f"Error calculating value area: {e}")
            return None


class HybridRangeDiscovery:
    """
    Main range discovery class combining KDE and volume profile analysis
    Implements whale behavior detection and range adjustment rules
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.kde = KernelDensityEstimator(config)
        self.volume_analyzer = VolumeProfileAnalyzer(config)
        
        # Whale detection placeholder (to be implemented)
        self.whale_confidence_threshold = 0.70
        
    async def discover_range(
        self, 
        price_data: np.ndarray, 
        volume_data: np.ndarray,
        market_regime: str = "NORMAL"
    ) -> Dict[str, any]:
        """
        Main range discovery method combining all techniques
        
        Args:
            price_data: Historical price data
            volume_data: Historical volume data
            market_regime: Current market regime
            
        Returns:
            Comprehensive range analysis
        """
        try:
            # 1. Base KDE range estimation
            kde_range = self.kde.estimate_range(price_data)
            
            # 2. Volume profile analysis
            volume_profile = self.volume_analyzer.analyze_volume_profile(
                price_data, volume_data
            )
            
            # 3. Whale behavior detection (placeholder)
            whale_adjustment = await self._detect_whale_behavior()
            
            # 4. Apply adjustment rules based on market conditions
            final_range = self._apply_adjustment_rules(
                kde_range, volume_profile, whale_adjustment, market_regime
            )
            
            # 5. Add metadata
            final_range.update({
                'timestamp': datetime.utcnow().isoformat(),
                'data_points': len(price_data),
                'volume_profile': volume_profile,
                'whale_adjustment': whale_adjustment
            })
            
            logger.info(
                f"Range discovery complete: {final_range['lower']:.4f} - "
                f"{final_range['upper']:.4f} (method: {final_range['method']})"
            )
            
            return final_range
            
        except Exception as e:
            logger.error(f"Error in range discovery: {e}")
            # Return safe fallback range
            current_price = price_data[-1] if len(price_data) > 0 else 100.0
            return {
                'lower': current_price * 0.95,
                'upper': current_price * 1.05,
                'center': current_price,
                'range_pct': 0.10,
                'confidence': 0.30,
                'method': 'error_fallback',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _detect_whale_behavior(self) -> Dict[str, any]:
        """
        Detect whale behavior patterns
        Placeholder implementation - full implementation in temporal module
        """
        # TODO: Implement actual whale detection
        return {
            'detected': False,
            'pattern': None,
            'confidence': 0.0,
            'adjustment_factor': 1.0
        }
    
    def _apply_adjustment_rules(
        self,
        kde_range: Dict[str, float],
        volume_profile: Dict[str, any],
        whale_adjustment: Dict[str, any],
        market_regime: str
    ) -> Dict[str, any]:
        """Apply range adjustment rules based on market conditions"""
        
        # Start with KDE range
        lower = kde_range['lower']
        upper = kde_range['upper']
        center = kde_range['center']
        
        # Whale adjustments
        if whale_adjustment['detected']:
            adjustment_factor = whale_adjustment['adjustment_factor']
            if whale_adjustment['pattern'] == 'accumulation':
                # Expand range upward for whale accumulation
                upper *= 1.15
                lower *= 1.05
            elif whale_adjustment['pattern'] == 'distribution':
                # Shift range downward for whale distribution
                upper *= 0.95
                lower *= 0.85
        
        # Market regime adjustments
        if market_regime == "HIGH_VOL_RANGE":
            # Add buffer for high volatility
            range_expansion = 1.10
            lower *= (2 - range_expansion)  # Expand downward
            upper *= range_expansion        # Expand upward
        elif market_regime == "TRENDING":
            # Reduce range in trending markets
            range_reduction = 0.80
            mid_point = (upper + lower) / 2
            range_size = (upper - lower) * range_reduction
            lower = mid_point - range_size / 2
            upper = mid_point + range_size / 2
        
        # Volume profile adjustments
        if volume_profile.get('poc'):
            # Bias range toward Point of Control
            poc = volume_profile['poc']
            if poc < lower or poc > upper:
                # Shift range to include POC
                range_size = upper - lower
                if poc < lower:
                    lower = poc - range_size * 0.3
                    upper = poc + range_size * 0.7
                else:
                    lower = poc - range_size * 0.7
                    upper = poc + range_size * 0.3
        
        return {
            'lower': lower,
            'upper': upper,
            'center': center,
            'range_pct': (upper - lower) / center,
            'confidence': min(kde_range['confidence'] * 
                            (1 + whale_adjustment['confidence']), 0.95),
            'method': f"hybrid_{kde_range['method']}"
        }
