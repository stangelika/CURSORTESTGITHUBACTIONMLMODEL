#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("=== TensorFlow GPU Test ===")
try:
    import tensorflow as tf
    print(f"✅ TensorFlow version: {tf.__version__}")
    print(f"✅ Built with CUDA: {tf.test.is_built_with_cuda()}")
    
    # Список физических устройств
    physical_devices = tf.config.list_physical_devices()
    print(f"✅ Physical devices: {len(physical_devices)}")
    for device in physical_devices:
        print(f"   - {device}")
    
    # GPU устройства
    gpus = tf.config.list_physical_devices('GPU')
    print(f"✅ GPU devices found: {len(gpus)}")
    for i, gpu in enumerate(gpus):
        print(f"   GPU {i}: {gpu}")
        
    if len(gpus) > 0:
        # Тест простого вычисления на GPU
        print("🧪 Testing GPU computation...")
        with tf.device('/GPU:0'):
            a = tf.constant([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
            b = tf.constant([[7.0, 8.0], [9.0, 10.0], [11.0, 12.0]])
            c = tf.matmul(a, b)
            result = c.numpy()
            print(f"✅ GPU computation result:\n{result}")
    else:
        print("❌ No GPU devices found - TensorFlow running on CPU only")
        
    print("✅ TensorFlow test completed successfully")
        
except ImportError as e:
    print(f"❌ TensorFlow not installed: {e}")
except Exception as e:
    print(f"❌ TensorFlow error: {e}")

print("=== End Test ===")
