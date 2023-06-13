# Recommendation System - IdeKita 
Source code and documentation of the Machine Learning team on the "IdeKita" Bangkit Capstone Project.

we are developing model using scraping dataset in omdena.com, after that we defining our database using the structure, so the model can running with the same structure

## Dataset
Our dataset basicly is scraping data from omdena.com with format look like this 

project.csv 
| Idproject | Project Title                                       | Categories                                         |
|-----------|-----------------------------------------------------|----------------------------------------------------|
| 6688      | House Price Recommendation System Using Machine Learning                                                       | Machine Learning \| NLP                             |
| 8345      | Creating a Text Summarization Tool to Combat the Overload of Information                                      | Data Science \| Machine Learning \| NLP              |
| 5000      | Tackling Deforestation in Tanzania with AI: A Mangrove-focused Pilot Project for National Carbon Monitoring | Data Science \| Machine Learning                    |
| 4143      | Geo-Tagging Nigerian License Plates Using Python and Computer Vision Through Machine Learning              | Computer Vision \| Geospatial Data Science \| Machine Learning |
---
ratings.csv
| Iduser | Idproject | Ratings | Timestamp    |
|--------|-----------|---------|--------------|
| 9983   | 6688      | 4       | 1658841756   |
| 9983   | 8345      | 3       | 1658841762   |
| 9983   | 5000      | 2       | 1658841769   |
| 7236   | 4143      | 4       | 1658841776   |
| 7236   | 4550      | 3       | 1658841783   |
| 7236   | 5913      | 4       | 1658841790   |
| 8150   | 3389      | 3       | 1658841797   |
| 8150   | 6841      | 4       | 1658841804   |
| 8150   | 6881      | 4       | 1658841811   |
---
user.csv
| Iduser | pref_categories                      |
| ------ | ----------------------------------- |
| 9983   | Machine Learning \| Deep Learning   |
| 7236   | Computer Vision \| Machine Learning |


## Notebook 
https://colab.research.google.com/drive/1HheA3wv5tTBpXdGLyWpzIMHuaYDF4gJy?usp=sharing

## Installation

To install and run the project locally, follow these steps:

1. Clone the repository:

    ```bash
    git clone https://github.com/idekita/machine-learning.git
    ```

2. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Configure the project:

    - Update the `config.py` file with the appropriate database connection details (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`), Google Cloud Storage credentials (`CREDENTIALS_PATH`), and other required configurations.

4. Set up the MySQL database:

    - Create a new MySQL database and import the necessary tables using the provided SQL script.

5. Run the application:

    ```bash
    python app.py
    ```

6. Access the application in your browser at [http://localhost:5000](http://localhost:5000).


## Configuration

The following configurations need to be set in the `config.py` file:

- `DB_HOST`: The hostname of the MySQL database server.
- `DB_USER`: The username to connect to the MySQL database.
- `DB_PASSWORD`: The password for the MySQL database user.
- `DB_NAME`: The name of the MySQL database.
- `CREDENTIALS_PATH`: The file path to the Google Cloud Storage credentials.
- `BUCKET_NAME`: The name of the Google Cloud Storage bucket.

## API Endpoints

### Database to CSV
The application provides the following API endpoints:

- `/`: Converts the database into a CSV format and returns the CSV file.
- `/recommendations` (POST): Triggers the recommendation process by fetching data from the database, performing recommendations using a machine learning model, and inserting the recommendations into the database.

#### / Endpoint

**Method:** GET

**Request Parameters:** None

**Request Body:** None

**Response:** Text

**Response Codes:**

- 200: Database converted to CSV and uploaded to Cloud Storage.


**Example Request:**

```bash
curl http://localhost:5000/
```

**Example Response:**
```bash
Database converted to CSV and uploaded to Cloud Storage
```

#### /recommendations Endpoint

**Method:** POST

**Request Parameters:** None

**Request Body:** None

**Response:** Text

**Response Codes:**

- 200: Recommendations were inserted into the database successfully.

**Example Request:**

```bash
curl -X POST http://localhost:5000/recommendations
```

**Example Response:***
```bash
Recommendations inserted into the database successfully!
```


## Recommendation Algorithm

The application uses a machine learning model (`recommendation.h5`) to generate recommendations for users based on their preferences and ratings data. The algorithm follows these steps:

1. Fetch user preferences, ratings data, and project data from the MySQL database.
2. Preprocess the data and map user and project IDs to indices.
3. Iterate over each user:
   - Check if the user exists in the ratings data and the mapping dictionary.
   - Split the user's preferred categories.
   - Select projects that match the user's preferred categories.
   - Predict ratings for the unwatched projects using the machine learning model.
   - Sort the projects based on predicted ratings.
   - Insert the recommendations into the database.
4. Return the recommendations.


## Project Structure
.

├── app.py : The main Flask application file.

├── config.py : Configuration file for the project.

├── credential.json : JSON file containing Google Cloud Storage credentials.

├── model

│   └── recommendation.h5 : The machine learning model for recommendations.

├── requirements.txt : File listing the required Python dependencies.

└── Dockerfile : File for building a Docker image of the application.



Certainly! Here's the updated version with the text inside a bash code block:


## Usage Examples

To use the application, follow these steps:

1. Ensure that the MySQL database is set up and running.
2. Update the `config.py` file with the appropriate database connection details and the path to the Google Cloud Storage credentials file (`credential.json`).
3. Install the required Python dependencies by running the following command:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the application by running the following command:

   ```bash
   python app.py
   ```

5. Access the application in your browser at [http://localhost:5000](http://localhost:5000).

To trigger the recommendation process, send a POST request to the `/recommendations` endpoint of the application. Here's an example using Python's `requests` library:

```bash
import requests

response = requests.post("http://localhost:5000/recommendations")
if response.status_code == 200:
    print("Recommendations inserted into the database successfully!")
else:
    print("Error: Failed to insert recommendations.")

```

## Local Deployment

To deploy the Flask application, you can use Docker. Here's an example of how to build a Docker image and run the container:

1. Make sure Docker is installed on your machine.
2. Create a `Dockerfile` with the following content:

   ```Dockerfile
   FROM python:3.9

   WORKDIR /app

   COPY . /app

   RUN pip install -r requirements.txt

   EXPOSE 5000

   CMD ["python", "app.py"]
   ```

3. Build the Docker image by running the following command in the project's root directory:

   ```bash
   docker build -t recommendation-app .
   ```

4. Run the Docker container using the image:

   ```bash
   docker run -p 5000:5000 recommendation-app
   ```

5. Access the application in your browser at [http://localhost:5000](http://localhost:5000).


## Deploy GCP with docker

Certainly! Here's the continuation of the development process with cloud deployment using Google Cloud Platform (GCP).

## Cloud Deployment with Google Cloud Platform (GCP)

To deploy the application on GCP, follow these steps:

1. Create a new project on GCP.

2. Enable the necessary APIs:
   - Google Cloud Storage API
   - Google Cloud SQL API

3. Set up the MySQL database on Google Cloud SQL:
   - Create a new Cloud SQL instance.
   - Create a database within the instance.
   - Import the necessary tables using the structure given.
   
4. Update the `config.py` file with and get the credential at services account gcp.

5. Build a Docker image of the application as explained in the previous section.

6. Push the Docker image to Google Container Registry (GCR)
   - Authenticate with GCR:
     ```bash
     gcloud auth configure-docker
     ```
   - Tag the Docker image:
     ```bash
     docker tag recommendation-app gcr.io/[PROJECT_ID]/recommendation-app
     ```
   - Push the Docker image to GCR:
     ```bash
     docker push gcr.io/[PROJECT_ID]/recommendation-app
     ```

8. Deploy the application on Google Cloud Run:
   - Deploy the Docker image to Cloud Run:
     ```bash
     gcloud run deploy recommendation-app --image gcr.io/[PROJECT_ID]/recommendation-app --platform managed
     ```
     if you can use the gcloud function, install the gcloud sdk first at https://cloud.google.com/sdk/docs/install
   - Follow the prompts to select the region, allow unauthenticated invocations, and choose a service name.
   
9. Once the deployment is successful, you will receive a URL for the deployed Cloud Run service.

10. Access the application in your browser using the provided URL.

Now your application is deployed on GCP, utilizing Google Cloud Storage and Google Cloud SQL for storage and database services respectively. Users can access the application using the provided external IP address.

Note: Make sure to replace `[PROJECT_ID]` with your actual GCP project ID throughout the steps.


## Troubleshooting

If you encounter any issues while setting up or using the application, consider the following:

- Verify that the MySQL database connection details in `config.py` are correct.
- Make sure the required Python dependencies are installed by running `pip install -r requirements.txt`.
- Ensure that the `credential.json` file exists.
