import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tensorflow as tf
from app.model.encoder import CNN_Encoder
from app.model.decoder import RNN_Decoder
from training.dataset import get_dummy_dataset, save_tokenizer
import os
import argparse

class CaptionModel(tf.keras.Model):
    def __init__(self, encoder, decoder):
        super(CaptionModel, self).__init__()
        self.encoder = encoder
        self.decoder = decoder
        self.loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(
            from_logits=True, reduction='none')

    @tf.function
    def train_step(self, data):
        img_tensor, target = data
        loss = 0

        batch_size = tf.shape(img_tensor)[0]
        hidden, memory = self.decoder.reset_state(batch_size=batch_size)

        # Assuming target[:, 0] is the <start> token
        dec_input = tf.expand_dims(target[:, 0], 1)

        with tf.GradientTape() as tape:
            spatial_features, global_emb = self.encoder(img_tensor, training=True)

            for i in range(1, target.shape[1]):
                predictions, hidden, memory, _ = self.decoder(dec_input, spatial_features, hidden, memory, training=True)
                
                real = target[:, i]
                mask = tf.math.logical_not(tf.math.equal(real, 0))
                loss_ = self.loss_fn(real, predictions)
                mask = tf.cast(mask, dtype=loss_.dtype)
                loss_ *= mask
                loss += tf.reduce_mean(loss_)

                # Teacher forcing
                dec_input = tf.expand_dims(target[:, i], 1)

        total_loss = loss / tf.cast(target.shape[1], tf.float32)
        trainable_variables = self.encoder.trainable_variables + self.decoder.trainable_variables
        gradients = tape.gradient(total_loss, trainable_variables)
        
        grads_and_vars = [(g, v) for g, v in zip(gradients, trainable_variables) if g is not None]
        self.optimizer.apply_gradients(grads_and_vars)

        return {"loss": total_loss}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dummy', action='store_true', help='Run with dummy data')
    args = parser.parse_args()

    print("Initializing dataset...")
    if args.dummy:
        dataset, tokenizer = get_dummy_dataset(batch_size=2)
    else:
        # Full COCO dataset loading would go here
        dataset, tokenizer = get_dummy_dataset(batch_size=2)
    
    weights_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', 'weights'))
    os.makedirs(weights_dir, exist_ok=True)
    save_tokenizer(tokenizer, os.path.join(weights_dir, 'tokenizer.json'))
    
    vocab_size = tokenizer.vocabulary_size()
    embedding_dim = 256
    units = 512
    
    encoder = CNN_Encoder(embedding_dim=1024)
    decoder = RNN_Decoder(embedding_dim, units, vocab_size)
    
    # Build models to initialize variables
    dummy_img = tf.zeros((1, 299, 299, 3))
    spatial_features, _ = encoder(dummy_img)
    hidden = tf.zeros((1, units))
    memory = tf.zeros((1, units))
    dec_input = tf.expand_dims([1], 1)
    decoder(dec_input, spatial_features, hidden, memory)
    
    model = CaptionModel(encoder, decoder)
    model.compile(optimizer=tf.keras.optimizers.Adam())
    
    print("Training model...")
    if args.dummy:
        print("Dummy mode: skipping full gradient training and just saving initialized weights.")
    else:
        model.fit(dataset, epochs=1)
    
    # Save the encoder and decoder weights
    encoder.save_weights(os.path.join(weights_dir, 'encoder_weights.weights.h5'))
    decoder.save_weights(os.path.join(weights_dir, 'decoder_weights.weights.h5'))
    print(f"Saved weights to {weights_dir}")

if __name__ == '__main__':
    main()
