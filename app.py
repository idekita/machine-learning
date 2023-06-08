import os
import numpy as np
import pandas as pd
import tensorflow as tf
from flask import Flask, jsonify, request
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

# Load the SavedModel
model = tf.keras.models.load_model('model/recommendation.h5')

# Mapping dictionaries
user_to_index = {user_id: index for index, user_id in enumerate(ratings_data['userId'].unique())}
movie_to_index = {movie_id: index for index, movie_id in enumerate(ratings_data['movieId'].unique())}

# Define Flask app
app = Flask(__name__)

# Define the prediction route
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json

    user_id = data['user_id']
    selected_categories = data['selected_categories']

    # Find movies that the user hasn't watched and belong to the selected categories
    unwatched_movies = ratings_data[~ratings_data['movieId'].isin(ratings_data[ratings_data['userId'] == user_id]['movieId'])]
    selected_movies = movies_data[movies_data['genres'].apply(lambda x: any(category in x for category in selected_categories))]

    # Merge unwatched movies and selected movies data
    filtered_movies = unwatched_movies.merge(selected_movies, on='movieId')

    # Remove duplicates based on movie titles
    filtered_movies = filtered_movies.drop_duplicates(subset='title')

    # Create arrays of user indices and movie indices for the unwatched movies in the selected categories
    user_indices = np.full(len(filtered_movies), user_to_index[user_id])
    movie_indices = filtered_movies['movieId'].map(movie_to_index).values

    # Make rating predictions using the model
    predicted_ratings = model.predict([user_indices, movie_indices]).flatten()

    # Merge unwatched movies with their predicted ratings
    filtered_movies['predicted_rating'] = predicted_ratings

    # Sort movies based on predicted ratings in descending order
    recommended_movies = filtered_movies.sort_values('predicted_rating', ascending=False).head(10)

    # Return the recommended movies as JSON response
    recommendations = recommended_movies[['title', 'genres', 'predicted_rating']]
    recommendations_json = recommendations.to_json(orient='records')
    
    return jsonify(recommendations_json)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
