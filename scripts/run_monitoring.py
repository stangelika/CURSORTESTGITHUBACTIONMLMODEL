#!/usr/bin/env python3
"""
ML Monitoring Script
Мониторинг ML процессов с логированием в течение заданного времени.
"""

import argparse
import os
import sys
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def setup_logging(log_dir="logs"):
    """Настройка дополнительного логирования в файл"""
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(log_path / "monitoring.txt")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    logger.addHandler(file_handler)

def monitor_system(duration_hours=72):
    """
    Основная функция мониторинга системы
    
    Args:
        duration_hours (int): Продолжительность мониторинга в часах
    """
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=duration_hours)
    
    logger.info(f"🚀 Запуск мониторинга на {duration_hours} часов")
    logger.info(f"📅 Начало: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📅 Окончание: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    iteration = 0
    
    try:
        while datetime.now() < end_time:
            iteration += 1
            current_time = datetime.now()
            remaining_time = end_time - current_time
            
            # Логирование статуса каждые 10 минут
            if iteration % 60 == 1:  # каждый час при интервале 10 секунд
                logger.info(f"📊 Итерация {iteration}")
                logger.info(f"⏰ Время: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"⏳ Осталось: {str(remaining_time).split('.')[0]}")
                
                # Здесь можно добавить проверки ML модели, метрики и т.д.
                # Например:
                # - Проверка доступности API
                # - Мониторинг использования GPU/CPU
                # - Проверка качества предсказаний
                # - Анализ логов ошибок
            
            # Спим 10 секунд между проверками
            time.sleep(10)
    
    except KeyboardInterrupt:
        logger.info("⚠️ Мониторинг прерван пользователем")
    except Exception as e:
        logger.error(f"❌ Ошибка в процессе мониторинга: {str(e)}")
        return 1
    
    logger.info("✅ Мониторинг завершен успешно")
    return 0

def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description='ML Monitoring Script')
    parser.add_argument(
        '--duration-hours', 
        type=int, 
        default=72,
        help='Продолжительность мониторинга в часах (по умолчанию: 72)'
    )
    parser.add_argument(
        '--log-dir',
        type=str,
        default='logs',
        help='Директория для логов (по умолчанию: logs)'
    )
    
    args = parser.parse_args()
    
    # Настройка логирования
    setup_logging(args.log_dir)
    
    # Запуск мониторинга
    return monitor_system(args.duration_hours)

if __name__ == "__main__":
    sys.exit(main())
