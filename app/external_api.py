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

def get_real_live_matches():
    try:
        url = "https://api.football-data.org/v4/competitions/WC/matches"
        headers = {'X-Auth-Token': os.getenv('API_KEY', '')}
        # Thử lấy trận đang đá, nếu không có lấy trận vừa kết thúc để demo
        params = {'status': 'IN_PLAY,PAUSED,FINISHED'}
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            return []
            
        data = response.json()
        matches = []
        
        for match in data.get('matches', []):
            status = match.get('status')
            home_team = match.get('homeTeam', {}).get('name')
            away_team = match.get('awayTeam', {}).get('name')
            score = match.get('score', {}).get('fullTime', {})
            home_score = score.get('home') if score.get('home') is not None else 0
            away_score = score.get('away') if score.get('away') is not None else 0
            minute = match.get('minute', 'FT' if status == 'FINISHED' else 'Live')
            
            matches.append({
                "match_id": match.get('id'),
                "status": status,
                "home_team": home_team or 'TBA',
                "away_team": away_team or 'TBA',
                "home_score": home_score,
                "away_score": away_score,
                "minute": minute
            })
            
            # Ưu tiên lấy các trận gần đây nhất
            if len(matches) >= 5:
                break
                
        # Sắp xếp các trận đang đá lên trên cùng
        matches.sort(key=lambda x: 0 if x['status'] in ['IN_PLAY', 'PAUSED'] else 1)
        return matches[:3]
    except Exception as e:
        logger.error(f"Error fetching live matches: {e}")
        return []

def get_real_match_lineup(match_id):
    try:
        url = f"https://api.football-data.org/v4/matches/{match_id}"
        headers = {'X-Auth-Token': os.getenv('API_KEY', '')}
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return None
            
        data = response.json()
        home_team = data.get('homeTeam', {})
        away_team = data.get('awayTeam', {})
        
        home_lineup = [p.get('name') for p in home_team.get('lineup', [])]
        away_lineup = [p.get('name') for p in away_team.get('lineup', [])]
        
        return {
            "home_name": home_team.get('name'),
            "away_name": away_team.get('name'),
            "home_lineup": home_lineup,
            "away_lineup": away_lineup
        }
    except Exception as e:
        logger.error(f"Error fetching lineup for {match_id}: {e}")
        return None

async def get_live_matches():
    return await asyncio.to_thread(get_real_live_matches)

async def get_match_lineup(match_id):
    return await asyncio.to_thread(get_real_match_lineup, match_id)
