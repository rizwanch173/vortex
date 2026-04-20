import requests

url = "https://tcf-backend.timescoursefinder.com/api/v2/search/courses_v2/"

params = {
    "pattern": "discipline/qualification",
    "discipline": "architecture",
    "degreelevel_type": "undergraduate",
    "page": 1
}

response = requests.get(url, params=params)

data = response.json()

courses = data["result"]

for course in courses:
    print(course["name"], "-", course["institute_name"])