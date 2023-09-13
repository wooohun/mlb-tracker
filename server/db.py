import requests
import pymongo
import dotenv
import datetime
import time
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

CONFIG = dotenv.dotenv_values('../mlb-tracker/.env.local')
CUR_YEAR = datetime.date.year

def get_date():
    cur_date = datetime.date
    return {"dd": cur_date.day, "mm": cur_date.month, "yyyy": cur_date.year}

def get_standings(year=CUR_YEAR):
    uri = f'https://api.sportradar.us/mlb/trial/v7/en/seasons/{year}/REG/standings.json?api_key={CONFIG["API_KEY"]}'
    
    try:
        res = requests.get(uri)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    
    res = res.json()
    return res['league']

def get_league_schedule(year=CUR_YEAR, season_type='REG'):
    uri = f'https://api.sportradar.us/mlb/trial/v7/en/games/{year}/{season_type}/schedule.json?api_key={CONFIG["API_KEY"]}'

    try:
        res = requests.get(uri)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    
    res = res.json()
    return res

def do_insert(doc):
    client = create_client()
    db = client.test

def create_client():

    uri = f"mongodb+srv://Woohun:wfv4zVSkgudg373s@cluster0.xzrabhp.mongodb.net/?retryWrites=true&w=majority"

    client = MongoClient(uri, server_api=ServerApi('1'))

    try:
        client.admin.command('ping')
        print('Connected')
    except Exception as e:
        print(e)

    return client

# def update_standings(doc):
#     db.standings.update_one(doc, {'$eq': {'id': data['id']}}, upsert=True)

# client = create_client()
# db = client.mlbDB
# standings_data = get_standings(2023)
# data = standings_data['season']
# standings = db.standings.insert_one(data)
# data = get_league_schedule(2023, 'REG')
# data['season']['games'] = data['games']
# data.pop('games')
# schedule = db.leagueSchedule.insert_one(data)
# schedule = db.leagueSchedule.insert_one(data)
# standings = db.standings.update_one(data, {'$eq': {'id': data['id']}}, upsert=True)

# print(db.list_collection_names())

def insert_schedule(year, sch_type):
    client = create_client()
    db = client.mlbDB
    schedule_data = get_league_schedule(year, sch_type)
    game_data = schedule_data.pop('games')
    for game in game_data:
        game['season_id'] = schedule_data['season']['id']

    schedule = db.leagueSchedule.insert_one(schedule_data)
    games = db.games.insert_many(game_data)



def insert_standings(year):
    client = create_client()
    db = client.mlbDB
    standings_data = get_standings(2023)

def get_team_ids():
    
    uri = f'http://api.sportradar.us/mlb/trial/v7/en/league/depth_charts.json?api_key={CONFIG["API_KEY"]}'

    try:
        res = requests.get(uri)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    
    res = res.json()
    team_ids = []
    for team in res['teams']:
        team_ids.append(team['id'])
    return team_ids

def get_team_profile(team_id):
    uri = f'http://api.sportradar.us/mlb/trial/v7/en/teams/{team_id}/profile.json?api_key={CONFIG["API_KEY"]}'
        
    try:
        res = requests.get(uri)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    res = res.json()
    return res


def insert_team_profiles():
    ids = get_team_ids()
    client = create_client()
    db = client.mlbDB

    for id in ids:
        res = get_team_profile(id)
        time.sleep(1)
        team = db.teamProfiles.insert_one(res)
        time.sleep(1)

def insert_player_profiles():
    client = create_client()
    db = client.mlbDB
    # teams = db.teamProfiles.find()
    # for team in teams:
    #     db.playerProfiles.insert_many(team['players'])
    
    players = db.playerProfiles.find()
    for player in players:
        cur = db.playerProfiles.find({"seasons": {"$exists": True}})
        if cur:
            continue
        time.sleep(2)
        uri = f'http://api.sportradar.us/mlb/trial/v7/en/players/{player["id"]}/profile.json?api_key={CONFIG["API_KEY"]}'

        try: 
            res = requests.get(uri)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
        res = res.json()
        res = res['player']
        # if "seasons" in res.keys():
        #     db.playerProfiles.update_one({'id': player["id"]}, {'$set': {'team': res["team"], 'seasons': res["seasons"]}})
        # else:
        #     db.playerProfiles.update_one({'id': player["id"]}, {'$set': {'team': res["team"]}})

def get_api_glossary():
    uri = f'http://api.sportradar.us/mlb/trial/v7/en/league/glossary.json?api_key={CONFIG["API_KEY"]}'

    try: 
        res = requests.get(uri)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    res = res.json()

    client = create_client()
    db = client.mlbDB
    db.glossary.insert_one(res)


