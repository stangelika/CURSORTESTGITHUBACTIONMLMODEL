#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("=== TensorFlow Test ===")
try:
    import tensorflow as tf
    print(f"✅ TensorFlow version: {tf.__version__}")
    print(f"✅ Built with CUDA: {tf.test.is_built_with_cuda()}")
    
    gpus = tf.config.list_physical_devices('GPU')
    print(f"✅ Physical GPUs found: {len(gpus)}")
    for i, gpu in enumerate(gpus):
        print(f"   GPU {i}: {gpu}")
        
    if len(gpus) > 0:
        # Тест простого вычисления на GPU
        with tf.device('/GPU:0'):
            a = tf.constant([[1.0, 2.0], [3.0, 4.0]])
            b = tf.constant([[5.0, 6.0], [7.0, 8.0]])
            c = tf.matmul(a, b)
            print(f"✅ GPU computation test: {c.numpy()}")
    else:
        print("❌ No GPU devices found")
        
except ImportError as e:
    print(f"❌ TensorFlow not installed: {e}")
except Exception as e:
    print(f"❌ TensorFlow error: {e}")

print("=== End Test ===")
