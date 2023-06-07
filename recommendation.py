import os
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MultiLabelBinarizer
from tensorflow import keras
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Embedding, Flatten, Input, Dot, Concatenate, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing import text_dataset_from_directory
from google.cloud import storage

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "submission-mgce-dhillen-13aadb34510e.json"

client = storage.Client()

bucket_name = 'project-img'
file_name1 = 'movies.csv'
file_name2 = 'ratings.csv'

bucket = client.get_bucket(bucket_name)
blob1 = bucket.blob(file_name1)
blob2 = bucket.blob(file_name2)

file_path = 'movies.csv'
blob1.download_to_filename(file_path)

file_path2 = 'ratings.csv'
blob2.download_to_filename(file_path2)

ratings_data = pd.read_csv(file_path2)
movies_data = pd.read_csv(file_path)

# Split data menjadi data latih dan data validasi
train_ratings, val_ratings = train_test_split(ratings_data, test_size=0.2, random_state=42)

# Ambil informasi jumlah user dan film
num_users = ratings_data['userId'].nunique()
num_movies = ratings_data['movieId'].nunique()

# Buat dictionary untuk mapping user dan film ke indeks numerik
user_to_index = {user_id: index for index, user_id in enumerate(ratings_data['userId'].unique())}
movie_to_index = {movie_id: index for index, movie_id in enumerate(ratings_data['movieId'].unique())}

# Buat kolom indeks untuk user dan film pada dataset
train_ratings['user_index'] = train_ratings['userId'].map(user_to_index)
train_ratings['movie_index'] = train_ratings['movieId'].map(movie_to_index)
val_ratings['user_index'] = val_ratings['userId'].map(user_to_index)
val_ratings['movie_index'] = val_ratings['movieId'].map(movie_to_index)

# Definisikan model rekomendasi menggunakan transfer learning
def collaborative_filtering_model(num_users, num_movies, embedding_dim=32):
    # Input layer
    user_input = Input(shape=(1,), name='user_input')
    movie_input = Input(shape=(1,), name='movie_input')

    # Embedding layer untuk user dan movie
    user_embedding = Embedding(num_users, embedding_dim, name='user_embedding')(user_input)
    movie_embedding = Embedding(num_movies, embedding_dim, name='movie_embedding')(movie_input)

    # Flatten embedding layer
    user_flatten = Flatten()(user_embedding)
    movie_flatten = Flatten()(movie_embedding)

    # Dot product antara user dan movie embedding
    dot_product = Dot(axes=1)([user_flatten, movie_flatten])

    # Concatenate user dan movie embedding
    concat = Concatenate()([user_flatten, movie_flatten])

    # Dropout layer
    dropout = Dropout(0.5)(concat)

    # Fully connected layer
    fc_layer = Dense(64, activation='relu')(dropout)
    output = Dense(1)(fc_layer)

    # Buat model
    model = Model(inputs=[user_input, movie_input], outputs=output)
    return model


# Inisialisasi model
model = collaborative_filtering_model(num_users, num_movies)

# Kompilasi model
model.compile(
    loss = 'mean_squared_error',
    optimizer = Adam(),
    metrics=[tf.keras.metrics.RootMeanSquaredError()]
)
#model.compile(optimizer=Adam(), loss='mean_squared_error')

# Training model
history = model.fit(
    x=[train_ratings['user_index'], train_ratings['movie_index']],
    y=train_ratings['rating'],
    validation_data=(
        [val_ratings['user_index'], val_ratings['movie_index']],
        val_ratings['rating']
    ),
    epochs=20,
    batch_size=64
)

tf.saved_model.save(model, "recommendation.h5")

# Contoh penggunaan model untuk memberikan rekomendasi film berdasarkan kategori yang dipilih oleh pengguna
user_id = 12
selected_categories = ['Adventure']

# Cari film yang belum ditonton oleh pengguna dan termasuk dalam kategori yang dipilih
unwatched_movies = ratings_data[~ratings_data['movieId'].isin(train_ratings[train_ratings['userId'] == user_id]['movieId'])]
selected_movies = movies_data[movies_data['genres'].apply(lambda x: any(category in x for category in selected_categories))]

# Gabungkan data film yang belum ditonton dan film yang termasuk dalam kategori yang dipilih
filtered_movies = unwatched_movies.merge(selected_movies, on='movieId')

# Hapus film dengan judul yang sudah ada sebelumnya
filtered_movies = filtered_movies.drop_duplicates(subset='title')

# Buat array indeks pengguna dan film yang belum ditonton dan termasuk dalam kategori yang dipilih
user_indices = np.full(len(filtered_movies), user_to_index[user_id])
movie_indices = filtered_movies['movieId'].map(movie_to_index).values

# Lakukan prediksi rating menggunakan model
predicted_ratings = model.predict([user_indices, movie_indices]).flatten()

# Gabungkan film yang belum ditonton dengan prediksi ratingnya
filtered_movies['predicted_rating'] = predicted_ratings

# Urutkan film berdasarkan prediksi rating secara menurun
recommended_movies = filtered_movies.sort_values('predicted_rating', ascending=False).head(10)

# Tampilkan rekomendasi film
print(recommended_movies[['title', 'genres', 'predicted_rating']])

