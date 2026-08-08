import tensorflow as tf
import numpy as np
import json
import os

def create_tokenizer(captions, top_k=5000):
    tokenizer = tf.keras.layers.TextVectorization(
        max_tokens=top_k,
        standardize='lower_and_strip_punctuation',
        split='whitespace',
        output_mode='int',
        output_sequence_length=30
    )
    # Add start and end tokens
    processed_captions = [f"<start> {caption} <end>" for caption in captions]
    tokenizer.adapt(processed_captions)
    return tokenizer

def save_tokenizer(tokenizer, save_path):
    # Save vocabulary
    vocab = tokenizer.get_vocabulary()
    with open(save_path, 'w') as f:
        json.dump(vocab, f)

def load_tokenizer(load_path, top_k=5000):
    with open(load_path, 'r') as f:
        vocab = json.load(f)
    tokenizer = tf.keras.layers.TextVectorization(
        max_tokens=top_k,
        standardize='lower_and_strip_punctuation',
        split='whitespace',
        output_mode='int',
        output_sequence_length=30,
        vocabulary=vocab
    )
    return tokenizer

def get_dummy_dataset(batch_size=2):
    # Create a tiny dummy dataset for pipeline verification
    # Images: (299, 299, 3) preprocessed shapes
    # Captions: string
    dummy_images = np.random.rand(10, 299, 299, 3).astype(np.float32)
    dummy_captions = ["a dog running on the grass"] * 10
    
    tokenizer = create_tokenizer(dummy_captions)
    
    processed_captions = [f"<start> {caption} <end>" for caption in dummy_captions]
    tokenized_captions = tokenizer(processed_captions)
    
    dataset = tf.data.Dataset.from_tensor_slices((dummy_images, tokenized_captions))
    dataset = dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)
    
    return dataset, tokenizer
