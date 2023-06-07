import requests

url = 'http://localhost:5000/predict'

data = {
    "user_id": 25,
    "selected_categories": ["Adventure", "Action"]
}

#                         send to endpoint                    encode json
# apps ----> id, kategori ----------------> json_rekomendasi -------------> list rekomendasi 

response = requests.post(url, json=data)

if response.status_code == 200:
    recommendations = response.json()
    print(recommendations)
else:
    print("Error:", response.status_code)
