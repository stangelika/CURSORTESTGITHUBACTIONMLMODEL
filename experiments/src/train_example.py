#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример тренировки модели на GPU с логированием и сохранением артефактов
"""

import os
import time
import json
from datetime import datetime
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

def create_experiment_dir(base_path="../results"):
    """Создает директорию для текущего эксперимента"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exp_dir = os.path.join(base_path, f"exp_{timestamp}")
    os.makedirs(exp_dir, exist_ok=True)
    os.makedirs(os.path.join(exp_dir, "checkpoints"), exist_ok=True)
    os.makedirs(os.path.join(exp_dir, "logs"), exist_ok=True)
    return exp_dir

class SimpleCNN(nn.Module):
    """Простая CNN для CIFAR-10/MNIST"""
    def __init__(self, num_classes=10):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 8 * 8, 512)  # для CIFAR-10 32x32
        self.fc2 = nn.Linear(512, num_classes)
        self.dropout = nn.Dropout(0.5)
        
    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = x.view(-1, 64 * 8 * 8)
        x = self.dropout(torch.relu(self.fc1(x)))
        x = self.fc2(x)
        return x

def train_model(num_epochs=5, batch_size=32, learning_rate=0.001):
    """Основная функция тренировки"""
    
    # Проверка GPU
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"🚀 Using device: {device}")
    if torch.cuda.is_available():
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    # Создание директории эксперимента
    exp_dir = create_experiment_dir()
    print(f"📁 Experiment directory: {exp_dir}")
    
    # Конфигурация эксперимента
    config = {
        "timestamp": datetime.now().isoformat(),
        "device": str(device),
        "num_epochs": num_epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "model": "SimpleCNN",
        "dataset": "CIFAR-10"
    }
    
    # Сохранение конфигурации
    with open(os.path.join(exp_dir, "config.json"), "w") as f:
        json.dump(config, f, indent=2)
    
    # Подготовка данных (заглушка для быстрого тестирования)
    print("📊 Preparing data...")
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    
    # Создание модели
    model = SimpleCNN(num_classes=10).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    print(f"🧠 Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Лог файл
    log_file = os.path.join(exp_dir, "logs", "training.log")
    
    # Симуляция тренировки (для быстрого тестирования)
    print("🏃 Starting training simulation...")
    training_log = []
    
    for epoch in range(num_epochs):
        epoch_start = time.time()
        
        # Симуляция forward/backward pass на GPU
        dummy_input = torch.randn(batch_size, 3, 32, 32).to(device)
        dummy_target = torch.randint(0, 10, (batch_size,)).to(device)
        
        optimizer.zero_grad()
        outputs = model(dummy_input)
        loss = criterion(outputs, dummy_target)
        loss.backward()
        optimizer.step()
        
        epoch_time = time.time() - epoch_start
        loss_val = loss.item()
        
        # Логирование
        log_entry = {
            "epoch": epoch + 1,
            "loss": loss_val,
            "time": epoch_time,
            "gpu_memory": torch.cuda.memory_allocated(device) / 1024**2 if torch.cuda.is_available() else 0
        }
        training_log.append(log_entry)
        
        print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss_val:.4f}, Time: {epoch_time:.2f}s")
        
        # Сохранение чекпоинта каждые несколько эпох
        if (epoch + 1) % 2 == 0:
            checkpoint = {
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': loss_val,
            }
            torch.save(checkpoint, os.path.join(exp_dir, "checkpoints", f"checkpoint_epoch_{epoch+1}.pth"))
    
    # Сохранение финальной модели
    torch.save(model.state_dict(), os.path.join(exp_dir, "final_model.pth"))
    
    # Сохранение лога тренировки
    with open(log_file, "w") as f:
        json.dump(training_log, f, indent=2)
    
    print(f"✅ Training completed! Results saved to: {exp_dir}")
    print(f"📋 Artifacts: config.json, final_model.pth, checkpoints/, logs/training.log")
    
    return exp_dir, training_log

if __name__ == "__main__":
    print("🔥 PyTorch GPU Training Example")
    print("=" * 50)
    
    # Быстрый тест для проверки
    exp_dir, log = train_model(num_epochs=3, batch_size=16)
    
    print("\n📊 Training Summary:")
    for entry in log:
        print(f"  Epoch {entry['epoch']}: Loss={entry['loss']:.4f}, GPU Memory={entry['gpu_memory']:.1f}MB")
