import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = "https://v3.football.api-sports.io/fixtures"
headers = {
    'x-rapidapi-host': 'v3.football.api-sports.io',
    'x-rapidapi-key': os.getenv('RAPIDAPI_KEY', '')
}
querystring = {"league": "1", "season": "2026", "next": "5"}

try:
    response = requests.get(url, headers=headers, params=querystring)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.text[:500]) # Print first 500 chars to avoid flood
except Exception as e:
    print("Error:", e)
