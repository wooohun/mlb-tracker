import requests
import pymongo
import dotenv
import datetime
import time
import pandas as pd
import json
from bson.objectid import ObjectId
from collections import defaultdict
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from scraper import add_statcast, compile_player_data, get_batter_ranks

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

def get_player_profile(p_id):
    time.sleep(1)
    uri = f'http://api.sportradar.us/mlb/trial/v7/en/players/{p_id}/profile.json?api_key={CONFIG["API_KEY"]}'

    try:
        res = requests.get(uri)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    
    jsn = json.loads(res.text)
    df = pd.DataFrame.from_dict(jsn['player'], orient='index').transpose()
    data = df.rename(
        columns={
            'first_name': 'f_name',
            'last_name': 'l_name',
            'height': 'ht',
            'weight': 'wt',
            'full_name': 'nameFull',
            'throw_hand': 'throws',
            'bat_hand': 'bats',
            'birthcity': 'birthCity',
            'birthcountry': 'birthCountry',
            'birthdate': 'birthDate',
            'reference': 'mlbamID'
        }
    ).to_json(orient='index')
    data = list(json.loads(data).values())[0]
    return data


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
    
    players = compile_player_data()
    for player in players:

        if 'pitching' not in player['seasons'][0].keys():
            continue
        player['statcast'] = add_statcast(player)

        updates = []
        
        for field in player.keys():  
            update = {
                '$set': {
                    field: player[field]
                }
            }
            updates.append(update)
        updates.append({
            '$set': {
                'updated': datetime.datetime.now()
            }
        })
        inserted_player = db.playerProfiles.update_one(
            {'mlbamID': player["mlbamID"]}, 
            updates,
        )
        print(f'Updated {inserted_player.modified_count} document(s)')
        time.sleep(1)
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
    
"""
    Used to Find 40-man roster for each team per season

    Manually limited to 2023 season for now due to API rate limits
"""
def insert_splits():
    client = create_client()
    db = client.mlbDB
    teams = db.teamProfiles.find(projection=['abbr', 'id'])
    for team in teams:
        for year in [2021]:
            time.sleep(1)
            team_id = team['id']
            query = db.splits.find_one({'id': team_id, 'season.year': year})
            if query:
                continue
            uri = f'http://api.sportradar.us/mlb/trial/v7/en/seasons/{year}/REG/teams/{team_id}/splits.json?api_key={CONFIG["API_KEY"]}'
            try:
                res = requests.get(uri)
            except requests.exceptions.RequestException as e:
                raise SystemExit(e)
            res = res.json()
            db.splits.insert_one(res)

def update_embedded_players_to_reference(year):
    client = create_client()
    db = client.mlbDB
    teams = db.splits.find({'season.year': year})
    for team in teams:
        for idx, player in enumerate(team['players']):
            query = None
            if '_id' in player.keys():
                continue
            query = db.playerProfiles.find_one({'id': player['id']})
            # if player profile doesnt exist in collection, grab data from api,
            # pass generated ObjectID to store as reference in splits document
            if query is None:
                new_player = get_player_profile(player['id'])
                id = new_player['id']
                _id = db.playerProfiles.insert_one(new_player).inserted_id
            else:
                _id = query['_id']
                id = query['id']
            db.splits.update_one(
                {'id': team['id'], 'season.year': team['season']['year']},
                {'$set': {f'players.{idx}': {'_id': _id, 'id': id}}}
            )
            print(f'Updated {team["season"]["year"]} {team["abbr"]}: {idx}')


insert_player_profiles()

