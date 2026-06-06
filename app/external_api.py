import os
import requests
import logging
import asyncio
import json
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Load stadium database from JSON file
stadium_map_path = os.path.join(os.path.dirname(__file__), 'stadium_map.json')
try:
    with open(stadium_map_path, 'r', encoding='utf-8') as f:
        STADIUM_DATABASE = json.load(f)
except FileNotFoundError:
    logger.warning("stadium_map.json not found. Using empty stadium mapping.")
    STADIUM_DATABASE = {}

def get_real_upcoming_matches():
    """
    Fetch real upcoming World Cup matches from Football-Data.org.
    """
    try:
        url = "https://api.football-data.org/v4/competitions/WC/matches"
        
        headers = {
            'X-Auth-Token': os.getenv('API_KEY', '')
        }
        
        params = {
            'status': 'SCHEDULED'
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 400:
            print("Token bị từ chối, hãy kiểm tra email xác thực")
            
        if response.status_code != 200:
            print(f"DEBUG - API Error: {response.text}")
            return []
            
        data = response.json()
        matches = []
        
        # Parse the JSON response
        for match in data.get('matches', []):
            status = match.get('status')
            if status in ['TIMED', 'SCHEDULED']:
                # Get venue, fallback to STADIUM_DATABASE, finally default to a professional string
                venue = match.get('venue')
                home_team_name = match.get('homeTeam', {}).get('name')
                
                if not venue or venue == "TBA" or venue == "null":
                    venue = STADIUM_DATABASE.get(home_team_name)
                    
                if not venue:
                    venue = 'Sân vận động chính thức (Thông tin đang cập nhật)'
                    
                match_dict = {
                    "match_id": match.get('id'),
                    "home_team": home_team_name or 'TBA',
                    "away_team": match.get('awayTeam', {}).get('name') or 'TBA',
                    "kickoff_time": match.get('utcDate'),
                    "stadium": venue
                }
                matches.append(match_dict)
                
                if len(matches) >= 5:
                    break
            
        return matches
        
    except Exception as e:
        logger.error(f"Error fetching data from Football-Data.org: {e}")
        return []

async def get_upcoming_matches():
    """
    Async wrapper to call the real API without blocking the Telegram Bot event loop.
    """
    # Use asyncio.to_thread to run the synchronous requests.get() in a separate thread
    return await asyncio.to_thread(get_real_upcoming_matches)
