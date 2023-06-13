import os
import numpy as np
import pandas as pd
import tensorflow as tf
import mysql.connector
from flask import Flask
from google.cloud import storage
from config import *
import csv

# Set up Flask app
app = Flask(__name__)

db = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

# Load the SavedModel
model = tf.keras.models.load_model("model/recommendation.h5")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_PATH
client = storage.Client()

def download_blob(file_name, file_path):
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(file_name)
    blob.download_to_filename(file_path)

def insert_recommendations(user_id, recommended_projects):
    cursor = db.cursor()

    # Delete existing recommendations for the user
    delete_query = "DELETE FROM recommendations WHERE id_user = %s"
    delete_values = (user_id,)
    cursor.execute(delete_query, delete_values)

    for index, row in recommended_projects.iterrows():
        project_id = row['Idproject']
        project_title = row['projecttitle']

        # Execute the INSERT query
        insert_query = "INSERT INTO recommendations (id_user, id_project, project_title) VALUES (%s, %s, %s)"
        values = (user_id, project_id, project_title)
        cursor.execute(insert_query, values)

    # Commit the changes to the database
    db.commit()

def get_recommendations(ratings_data, project_data, user_data, model):
    # Mapping dictionaries
    user_to_index = {user_id: index for index, user_id in enumerate(ratings_data['Iduser'].unique())}
    project_to_index = {project_id: index for index, project_id in enumerate(ratings_data['Idproject'].unique())}

    for index, row in user_data.iterrows():
        user_id = row['Iduser']
        pref_categories = row['pref_categories']

        if user_id not in ratings_data['Iduser'].unique() or user_id not in user_to_index:
            print(f"User ID {user_id} not found in ratings_data or user_to_index dictionary. Skipping recommendation.")
            continue

        if isinstance(pref_categories, str):
            selected_categories = pref_categories.split(' | ')

            train_ratings_user = ratings_data[ratings_data['Iduser'] != user_id]
            unwatched_projects = ratings_data[~ratings_data['Idproject'].isin(train_ratings_user[train_ratings_user['Iduser'] == user_id]['Idproject'])]
            selected_projects = project_data[project_data['categories'].apply(lambda x: any(category in x for category in selected_categories))]

            filtered_projects = unwatched_projects.merge(selected_projects, on='Idproject').drop_duplicates(subset='projecttitle')

            user_indices = np.full(len(filtered_projects), user_to_index[user_id])
            project_indices = filtered_projects['Idproject'].map(project_to_index).values

            if len(filtered_projects) > 0:
                # Lakukan prediksi rating menggunakan model
                predicted_ratings = model.predict([user_indices, project_indices]).flatten()

                # Gabungkan proyek yang belum dilihat dengan prediksi ratingnya
                filtered_projects['predicted_rating'] = predicted_ratings

                # Urutkan proyek berdasarkan prediksi rating secara menurun
                recommended_projects = filtered_projects.sort_values('predicted_rating', ascending=False).head(10)

                # insert rekomendasi proyek
                insert_recommendations(user_id, recommended_projects)
                print("Recommendation succesfull")
            else:
                print("No projects available for recommendation.")
        else:
            print(f"Invalid pref_categories for User ID {user_id}. Skipping recommendation.")

# Routes
@app.route('/')
def convert_to_csv():
    cursor = db.cursor()

    # Execute the SQL query to fetch the data from projects table
    query_projek = "SELECT projects.id_proyek AS Idproject, projects.nm_proyek AS projecttitle, categories.nm_kategori AS categories FROM projects INNER JOIN categories ON projects.id_kategori = categories.id_kategori;"
    cursor.execute(query_projek)
    data_projek = cursor.fetchall()

    # Execute the SQL query to fetch the data from ratings table
    query_ratings = "SELECT ratings.id_proyek AS Idproject, users.id_user AS Iduser, ratings.nilai AS ratings, UNIX_TIMESTAMP(ratings.updatedAt) AS timestamp FROM ratings INNER JOIN users ON ratings.username = users.username"
    cursor.execute(query_ratings)
    data_ratings = cursor.fetchall()

    query_pref = "SELECT id_user AS Iduser, pref_categories AS pref_categories FROM users"
    cursor.execute(query_pref)
    data_user = cursor.fetchall()

    # Export data to a CSV file with headers
    
    with open(projek, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['Idproject', 'projecttitle', 'categories'])  # Add header row
        csv_writer.writerows(data_projek)

    with open(ratings, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['Idproject', 'Iduser', 'ratings', 'timestamp'])  # Add header row
        csv_writer.writerows(data_ratings)

    with open(preferensi, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['Iduser', 'pref_categories'])  # Add header row
        csv_writer.writerows(data_user)

    # Upload the CSV files to Cloud Storage
    bucket = client.bucket(BUCKET_NAME)
    blob1 = bucket.blob(projek)
    blob2 = bucket.blob(ratings)
    blob3 = bucket.blob(preferensi)
    blob1.upload_from_filename(projek)
    blob2.upload_from_filename(ratings)
    blob3.upload_from_filename(preferensi)

    return 'Database converted to CSV and uploaded to Cloud Storage.'


@app.route('/recommendations', methods=['POST'])
def recommend_projects():
    download_blob(projek, 'project.csv')
    download_blob(ratings, 'ratings.csv')
    download_blob(preferensi, 'user.csv')

    ratings_data = pd.read_csv('ratings.csv')
    project_data = pd.read_csv('project.csv')
    user_data = pd.read_csv('user.csv')

    get_recommendations(ratings_data, project_data, user_data, model)

    return "Recommendations inserted into the database successfully!"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
