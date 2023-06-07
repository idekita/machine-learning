import os
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow import keras
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Embedding, Flatten, Input, Dot, Concatenate, Dense, Dropout
from tensorflow.keras.optimizers import Adam

# Load the trained model
model = keras.models.load_model('recommendation.h5')

# Define the serving function
@tf.function(input_signature=[tf.TensorSpec(shape=(None, 1), dtype=tf.int32, name='user_input'),
                              tf.TensorSpec(shape=(None, 1), dtype=tf.int32, name='movie_input')])
def serving_fn(user_input, movie_input):
    predicted_ratings = model([user_input, movie_input])
    return {'predicted_ratings': predicted_ratings}

# Convert the serving function to a TensorFlow SavedModel
user_input = tf.TensorSpec(shape=(None, 1), dtype=tf.int32, name='user_input')
movie_input = tf.TensorSpec(shape=(None, 1), dtype=tf.int32, name='movie_input')
tf.saved_model.save(model, './savedmodel', signatures={'serving_default': serving_fn.get_concrete_function(user_input, movie_input)})