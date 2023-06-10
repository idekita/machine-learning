import os
import numpy as np
import pandas as pd
import tensorflow as tf
import mysql.connector
from flask import Flask
from google.cloud import storage
from sklearn.model_selection import train_test_split

# Load the SavedModel
model = tf.keras.models.load_model("model/recommendation.h5")

# Set up Google Cloud Storage client
secret_key = os.environ['GCP_SA_KEY']
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = secret_key
client = storage.Client()

bucket_name = 'dataset-csv'
file_name1 = 'project.csv'
file_name2 = 'ratings.csv'
file_name3 = 'user.csv'

def download_blob(file_name, file_path):
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.download_to_filename(file_path)

def insert_recommendations(user_id, recommended_projects):
    db = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
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
    # Split data into training and validation sets
    train_ratings, val_ratings = train_test_split(ratings_data, test_size=0.2, random_state=42)

    # Get the number of users and projects
    num_users = ratings_data['Iduser'].nunique()
    num_projects = ratings_data['Idproject'].nunique()

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

            predicted_ratings = model.predict([user_indices, project_indices]).flatten()

            filtered_projects['predicted_rating'] = predicted_ratings

            recommended_projects = filtered_projects.sort_values('predicted_rating', ascending=False).head(10)

            insert_recommendations(user_id, recommended_projects)
        else:
            print(f"Invalid pref_categories for User ID {user_id}. Skipping recommendation.")

app = Flask(__name__)

@app.route('/recommendations', methods=['POST'])
def recommend_projects():
    download_blob(file_name1, 'project.csv')
    download_blob(file_name2, 'ratings.csv')
    download_blob(file_name3, 'user.csv')

    ratings_data = pd.read_csv('ratings.csv')
    project_data = pd.read_csv('project.csv')
    user_data = pd.read_csv('user.csv')

    get_recommendations(ratings_data, project_data, user_data, model)

    return "Recommendations inserted into the database successfully!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)