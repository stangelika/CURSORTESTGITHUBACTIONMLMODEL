#!/usr/bin/env python3
"""
GPU Monitoring Script for ML Workstation Automation

Monitors NVIDIA GPU usage during ML training sessions.
Logs GPU metrics to CSV for analysis and workflow artifacts.
"""

import argparse
import csv
import json
import os
import signal
import sys
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import pynvml
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GPUMonitor:
    """NVIDIA GPU monitoring with CSV logging."""
    
    def __init__(self, output_file: str = "gpu_usage.csv", interval: int = 60):
        self.output_file = Path(output_file)
        self.interval = interval
        self.running = False
        self.gpu_count = 0
        
        # Create output directory if needed
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize NVML if available
        if NVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.gpu_count = pynvml.nvmlDeviceGetCount()
                logger.info(f"NVML initialized. Found {self.gpu_count} GPU(s)")
            except Exception as e:
                logger.error(f"NVML initialization failed: {e}")
                # Can't modify global NVML_AVAILABLE, so just continue with fallback
        
        if not NVML_AVAILABLE:
            logger.warning("NVML not available. Will use nvidia-smi fallback")
            
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle termination signals gracefully."""
        logger.info(f"Received signal {signum}. Stopping monitoring...")
        self.running = False
    
    def get_gpu_info_smi(self) -> List[Dict]:
        """Get GPU info using nvidia-smi (fallback method)."""
        import subprocess
        
        try:
            # Run nvidia-smi with CSV format
            cmd = [
                'nvidia-smi',
                '--query-gpu=index,name,utilization.gpu,memory.used,memory.total,memory.free,temperature.gpu,power.draw,power.limit',
                '--format=csv,noheader,nounits'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                logger.error(f"nvidia-smi failed: {result.stderr}")
                return []
            
            gpu_info = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = [part.strip() for part in line.split(',')]
                    if len(parts) >= 9:
                        try:
                            gpu_info.append({
                                'gpu_id': int(parts[0]),
                                'name': parts[1],
                                'gpu_utilization': float(parts[2]) if parts[2] != '[Not Supported]' else None,
                                'memory_used_mb': float(parts[3]),
                                'memory_total_mb': float(parts[4]),
                                'memory_free_mb': float(parts[5]),
                                'memory_utilization': (float(parts[3]) / float(parts[4])) * 100,
                                'temperature_c': float(parts[6]) if parts[6] != '[Not Supported]' else None,
                                'power_draw_w': float(parts[7]) if parts[7] != '[Not Supported]' else None,
                                'power_limit_w': float(parts[8]) if parts[8] != '[Not Supported]' else None,
                                'timestamp': datetime.now().isoformat()
                            })
                        except ValueError as e:
                            logger.error(f"Error parsing nvidia-smi output: {e}")
            
            return gpu_info
            
        except subprocess.TimeoutExpired:
            logger.error("nvidia-smi command timed out")
        except FileNotFoundError:
            logger.error("nvidia-smi not found in PATH")
        except Exception as e:
            logger.error(f"nvidia-smi error: {e}")
            
        return []
    
    def get_gpu_info(self) -> List[Dict]:
        """Get GPU info using best available method."""
        return self.get_gpu_info_smi()
    
    def init_csv(self):
        """Initialize CSV file with headers."""
        headers = [
            'timestamp', 'gpu_id', 'name', 'gpu_utilization', 
            'memory_used_mb', 'memory_total_mb', 'memory_free_mb', 'memory_utilization',
            'temperature_c', 'power_draw_w', 'power_limit_w'
        ]
        
        with open(self.output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
        logger.info(f"CSV initialized: {self.output_file}")
    
    def log_gpu_info(self, gpu_info: List[Dict]):
        """Log GPU info to CSV file."""
        if not gpu_info:
            return
            
        with open(self.output_file, 'a', newline='') as f:
            writer = csv.writer(f)
            for gpu in gpu_info:
                writer.writerow([
                    gpu['timestamp'],
                    gpu['gpu_id'],
                    gpu['name'],
                    gpu['gpu_utilization'],
                    gpu['memory_used_mb'],
                    gpu['memory_total_mb'],
                    gpu['memory_free_mb'],
                    gpu['memory_utilization'],
                    gpu['temperature_c'],
                    gpu['power_draw_w'],
                    gpu['power_limit_w']
                ])
    
    def run(self, duration_hours: Optional[float] = None):
        """Run monitoring loop."""
        self.running = True
        self.init_csv()
        
        start_time = time.time()
        end_time = start_time + (duration_hours * 3600) if duration_hours else None
        
        logger.info(f"Starting GPU monitoring (interval: {self.interval}s)")
        if duration_hours:
            logger.info(f"Duration: {duration_hours} hours")
        else:
            logger.info("Duration: indefinite (Ctrl+C to stop)")
        
        iteration = 0
        while self.running:
            current_time = time.time()
            
            # Check duration limit
            if end_time and current_time >= end_time:
                logger.info("Duration limit reached. Stopping monitoring.")
                break
            
            # Get and log GPU info
            gpu_info = self.get_gpu_info()
            if gpu_info:
                self.log_gpu_info(gpu_info)
                
                # Log summary to console
                iteration += 1
                for gpu in gpu_info:
                    logger.info(
                        f"GPU{gpu['gpu_id']}: {gpu['gpu_utilization']}% util, "
                        f"{gpu['memory_utilization']:.1f}% mem, {gpu['temperature_c']}°C"
                    )
            else:
                logger.warning("No GPU info available")
            
            # Wait for next interval
            try:
                time.sleep(self.interval)
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
        
        elapsed = time.time() - start_time
        logger.info(f"Monitoring stopped. Total runtime: {elapsed:.1f}s, iterations: {iteration}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="GPU monitoring script for ML workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gpu_monitor.py --interval 30 --out gpu_usage.csv
  python gpu_monitor.py --duration 2.0 --interval 60
  python gpu_monitor.py --out logs/gpu_monitoring.csv --duration 72
        """
    )
    
    parser.add_argument(
        '--interval', 
        type=int, 
        default=60,
        help='Monitoring interval in seconds (default: 60)'
    )
    
    parser.add_argument(
        '--out', '--output',
        type=str, 
        default='gpu_usage.csv',
        help='Output CSV file path (default: gpu_usage.csv)'
    )
    
    parser.add_argument(
        '--duration',
        type=float,
        help='Duration in hours (default: run indefinitely)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run a quick test and exit'
    )
    
    args = parser.parse_args()
    
    # Test mode
    if args.test:
        monitor = GPUMonitor()
        gpu_info = monitor.get_gpu_info()
        if gpu_info:
            print("GPU Test Results:")
            print(json.dumps(gpu_info, indent=2))
            return 0
        else:
            print("No GPUs detected or nvidia-smi not available")
            return 1
    
    # Normal monitoring
    try:
        monitor = GPUMonitor(output_file=args.out, interval=args.interval)
        monitor.run(duration_hours=args.duration)
        return 0
    except Exception as e:
        logger.error(f"Monitoring failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())