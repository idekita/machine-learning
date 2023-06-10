import os
from flask import Flask, request
import csv
import mysql.connector
from google.cloud import storage

# ...
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "submission-mgce-dhillen-cb4aed65d427.json"

app = Flask(__name__)

# Database configuration
DB_HOST = '34.101.209.92'
DB_USER = 'root'
DB_PASSWORD = 'idekita'
DB_NAME = 'idekita'

# Cloud Storage configuration
BUCKET_NAME = 'dataset-csv'

@app.route('/')
def convert_to_csv():
    # Connect to the database
    db = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
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
    projek = 'project.csv'
    ratings = 'ratings.csv'
    preferensi = 'user.csv'
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




    # Upload the CSV file to Cloud Storage
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob1 = bucket.blob(projek)
    blob2 = bucket.blob(ratings)
    blob3 = bucket.blob(preferensi)
    blob1.upload_from_filename(projek)
    blob2.upload_from_filename(ratings)
    blob3.upload_from_filename(preferensi)

    return 'Database converted to CSV and uploaded to Cloud Storage.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500)
