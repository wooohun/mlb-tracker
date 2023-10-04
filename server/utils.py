import requests
import pymongo
import datetime
import json
import pybaseball as pb
from collections import defaultdict
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def create_client():

    uri = f"mongodb+srv://Woohun:wfv4zVSkgudg373s@cluster0.xzrabhp.mongodb.net/?retryWrites=true&w=majority"

    client = MongoClient(uri, server_api=ServerApi('1'))

    try:
        client.admin.command('ping')
        print('Connected')
    except Exception as e:
        print(e)

    return client

# Query: 
#       Tuple(str: l_name, str: f_name) -> Dict(full_dates: Tuple, years: Tuple)
def get_career_range(player_doc):
    debut_full = player_doc['pro_debut']
    
    today = datetime.date.today()
    today_full = today.strftime("%Y-%m-%d")
    return {'full': (debut_full, today_full), 'YYYY': (debut_full[:4], f'{today.year}')}

def reformat_seasons():
    client = create_client()
    db = client.mlbDB
    players = db.playerProfiles.find({}, projection={'_id': 0})
    for player in players:
        if 'seasons' not in player.keys():
            continue
        p_id = player['id']
        old_s = player['seasons']
        if type(old_s) == dict:
            continue
        new_s = defaultdict(list)
        for season in old_s:
            new_s[season['type']].append(season)
        db.playerProfiles.update_one(
            {'id': p_id},
            {'$set': {'seasons': new_s}})
        print(f'{player["preferred_name"]} {player["last_name"]} updated.')



def combine_b_day(row):
    year = int(row['birthYear'])
    month = int(row['birthMonth'])
    day = int(row['birthDay'])
    bday = datetime.datetime(year, month, day).strftime('%Y-%m-%d')

    return bday

"""
    Data pulled from Sean Lahman's Database, as made available by pybaseball

    Parameters: 
        player_bios: DataFrame
        bbref_id: str

    Returns Dict with keys:

"""
def get_player_bio(player_bios, id_fg, p_name):
    
    # get player with matching fangraphs id
    pids = pb.playerid_reverse_lookup([id_fg], key_type='fangraphs')
    if pids.empty:
        f_name, l_name = p_name.split(' ', 1)
        pids = pb.playerid_lookup(l_name, f_name)
        if pids.empty:
            return None
        else:
            pids['key_fangraphs'] = id_fg
    bio = player_bios[player_bios['bbrefID'] == pids['key_bbref'].item()].dropna(axis='columns', how='all')
    if bio.empty:
        return None
    bday = bio.apply(combine_b_day, axis=1)
    bio['birthDate'] = bday.item()
    bio = bio.drop(labels=[
        'birthYear',
        'birthMonth',
        'birthDay',
        'playerID'
    ], axis=1).rename(columns={
        'nameFirst': 'f_name',
        'nameLast': 'l_name',
        'weight': 'wt',
        'height': 'ht',
    })
    bio['mlbamID'] = pids['key_mlbam'].item()
    bio['nameFull'] = bio['f_name'].item() + ' ' + bio['l_name'].item()
    bio['fgID'] = pids['key_fangraphs'].item()
    jsn = bio.to_json(orient='index')
    data = list(json.loads(jsn).values())[0]
    return data

"""
    Parameters:
        l_name: str,
        f_name: str

    Returns DataFrame with following fields:

        name_last: str,
        name_first: str,
        key_mlbam: int,
        key_retro: str,
        key_bbref: str,
        key_fangraphs: int,
        mlb_played_first: float, 
        mlb_played_last: float

    mlb_played_first/last are floats representing year
"""
def get_player_ids(l_name, f_name):
    return pb.playerid_lookup(l_name, f_name)