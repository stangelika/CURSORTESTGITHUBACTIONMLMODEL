#!/usr/bin/env python3
"""
ML Training Template for GPU Validation

Basic PyTorch training script to validate GPU setup and workflow automation.
Designed for RTX 4060 with CUDA support and automated monitoring.
"""

import argparse
import json
import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class SimpleModel(nn.Module):
    """Simple neural network for demonstration."""
    
    def __init__(self, input_size: int = 100, hidden_size: int = 256, num_classes: int = 10):
        super(SimpleModel, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size // 2, num_classes)
        )
    
    def forward(self, x):
        return self.network(x)


def create_synthetic_data(num_samples: int = 10000, input_size: int = 100, num_classes: int = 10):
    """Create synthetic dataset for training demonstration."""
    
    # Generate random features
    X = torch.randn(num_samples, input_size)
    
    # Generate labels (some patterns for non-random learning)
    y = torch.randint(0, num_classes, (num_samples,))
    
    # Add some pattern to make training meaningful
    for i in range(num_classes):
        mask = y == i
        X[mask] += torch.randn(input_size) * 0.5  # Class-specific offset
    
    return X, y


def train_model(model, train_loader, criterion, optimizer, device, num_epochs: int = 10):
    """Training loop with progress logging."""
    
    model.train()
    training_stats = {
        'epochs': [],
        'losses': [],
        'accuracy': [],
        'gpu_memory': []
    }
    
    logger.info(f"Starting training for {num_epochs} epochs on {device}")
    
    for epoch in range(num_epochs):
        epoch_loss = 0.0
        correct = 0
        total = 0
        
        start_time = time.time()
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            
            # Calculate accuracy
            _, predicted = torch.max(output.data, 1)
            total += target.size(0)
            correct += (predicted == target).sum().item()
            
            # Log every 50 batches
            if batch_idx % 50 == 0 and batch_idx > 0:
                logger.info(f'Epoch {epoch+1}/{num_epochs}, Batch {batch_idx}, Loss: {loss.item():.4f}')
        
        epoch_time = time.time() - start_time
        epoch_accuracy = 100.0 * correct / total
        avg_loss = epoch_loss / len(train_loader)
        
        # GPU memory usage
        gpu_memory = 0
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.memory_allocated(device) / 1024 / 1024  # MB
        
        # Store stats
        training_stats['epochs'].append(epoch + 1)
        training_stats['losses'].append(avg_loss)
        training_stats['accuracy'].append(epoch_accuracy)
        training_stats['gpu_memory'].append(gpu_memory)
        
        logger.info(
            f'Epoch {epoch+1}/{num_epochs} completed in {epoch_time:.2f}s - '
            f'Loss: {avg_loss:.4f}, Accuracy: {epoch_accuracy:.2f}%, '
            f'GPU Memory: {gpu_memory:.1f}MB'
        )
        
        # Save checkpoint every 5 epochs
        if (epoch + 1) % 5 == 0:
            checkpoint_path = f'models/checkpoint_epoch_{epoch+1}.pth'
            torch.save({
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': avg_loss,
                'accuracy': epoch_accuracy
            }, checkpoint_path)
            logger.info(f'Checkpoint saved: {checkpoint_path}')
    
    return training_stats


def save_results(stats, device_info, args):
    """Save training results and system info."""
    
    results_dir = Path('results')
    results_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Training statistics
    stats_file = results_dir / f'training_stats_{timestamp}.json'
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    # System and run info
    run_info = {
        'timestamp': timestamp,
        'device': str(args.device),
        'epochs': args.epochs,
        'batch_size': args.batch_size,
        'learning_rate': args.learning_rate,
        'model_params': sum(p.numel() for p in device_info.get('model_params', [])),
        'system_info': device_info
    }
    
    info_file = results_dir / f'run_info_{timestamp}.json'
    with open(info_file, 'w') as f:
        json.dump(run_info, f, indent=2)
    
    logger.info(f'Results saved to {results_dir}/')
    return stats_file, info_file


def get_device_info():
    """Collect device and system information."""
    
    info = {
        'python_version': sys.version,
        'pytorch_version': torch.__version__,
        'cuda_available': torch.cuda.is_available(),
        'device_count': torch.cuda.device_count() if torch.cuda.is_available() else 0
    }
    
    if torch.cuda.is_available():
        info['cuda_version'] = torch.version.cuda
        info['cudnn_version'] = torch.backends.cudnn.version()
        
        for i in range(torch.cuda.device_count()):
            device_props = torch.cuda.get_device_properties(i)
            info[f'gpu_{i}'] = {
                'name': device_props.name,
                'memory_total': device_props.total_memory / 1024 / 1024,  # MB
                'multiprocessor_count': device_props.multi_processor_count,
                'major': device_props.major,
                'minor': device_props.minor
            }
    
    return info


def main():
    """Main training function."""
    
    parser = argparse.ArgumentParser(description='ML Training Template for GPU Validation')
    
    parser.add_argument('--device', type=str, default='auto',
                       help='Device to use (auto, cpu, cuda, cuda:0, etc.)')
    parser.add_argument('--epochs', type=int, default=20,
                       help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=128,
                       help='Training batch size')
    parser.add_argument('--learning-rate', type=float, default=0.001,
                       help='Learning rate')
    parser.add_argument('--num-samples', type=int, default=10000,
                       help='Number of synthetic samples')
    parser.add_argument('--save-model', action='store_true',
                       help='Save final model')
    
    args = parser.parse_args()
    
    # Determine device
    if args.device == 'auto':
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    else:
        device = torch.device(args.device)
    
    logger.info(f"Using device: {device}")
    
    # Get system info
    device_info = get_device_info()
    logger.info("System Information:")
    logger.info(json.dumps(device_info, indent=2))
    
    # Create directories
    Path('models').mkdir(exist_ok=True)
    Path('results').mkdir(exist_ok=True)
    
    # Create synthetic dataset
    logger.info("Creating synthetic dataset...")
    X, y = create_synthetic_data(args.num_samples)
    
    # Create data loader
    dataset = TensorDataset(X, y)
    train_loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)
    
    # Create model
    model = SimpleModel().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)
    
    device_info['model_params'] = [p for p in model.parameters()]
    total_params = sum(p.numel() for p in model.parameters())
    logger.info(f"Model created with {total_params} parameters")
    
    # Train model
    try:
        training_stats = train_model(model, train_loader, criterion, optimizer, device, args.epochs)
        
        # Save results
        stats_file, info_file = save_results(training_stats, device_info, args)
        
        # Save final model if requested
        if args.save_model:
            model_path = 'models/final_model.pth'
            torch.save({
                'model_state_dict': model.state_dict(),
                'model_config': {
                    'input_size': 100,
                    'hidden_size': 256,
                    'num_classes': 10
                },
                'training_stats': training_stats,
                'device_info': device_info
            }, model_path)
            logger.info(f'Final model saved: {model_path}')
        
        logger.info("Training completed successfully!")
        
        # Final summary
        final_accuracy = training_stats['accuracy'][-1]
        final_loss = training_stats['losses'][-1]
        logger.info(f"Final results - Loss: {final_loss:.4f}, Accuracy: {final_accuracy:.2f}%")
        
        return 0
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())