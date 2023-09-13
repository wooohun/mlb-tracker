import requests
import datetime
import dotenv
from .db import create_client

config = dotenv.dotenv_values('../mlb-tracker/.env.local')

def get_date():
    cur_date = datetime.date
    return {"dd": cur_date.day, "mm": cur_date.month, "yyyy": cur_date.year}

def get_standings(year):
    uri = f'https://api.sportradar.us/mlb/trial/v7/en/seasons/{year}/REG/standings.json?api_key={config["API_KEY"]}'
    
    try:
        res = requests.get(uri)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    
    res = res.json()
    return res['league']

def get_league_schedule(year, season_type):
    uri = f'https://api.sportradar.us/mlb/trial/v7/en/games/{year}/{season_type}/schedule.json?api_key={config["API_KEY"]}'

    try:
        res = requests.get(uri)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    
    res = res.json()
    return res['league']

def do_insert(doc):
    client = create_client()
    db = client.test

