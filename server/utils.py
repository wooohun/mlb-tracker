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


def get_annual_batting_ranks(year, season, mlbam_id):
    bat_pct_ranks = pb.statcast_batter_percentile_ranks(season['year']).dropna(axis='columns', how='all')
    sprint_spds = pb.statcast_sprint_speed(season['year'], 50)

    qual_sprint = sprint_spds[~sprint_spds.isnull().any(axis=1)]
    qual_bat = bat_pct_ranks[~bat_pct_ranks.isnull().any(axis=1)]

    bat_rank = qual_bat[qual_bat['player_id'] == mlbam_id].drop(
                    columns=[
                        'oaa',
                        'xiso',
                        'xobp',
                        'whiff_percent'
                    ]
                ).rename(
                    columns={
                        'player_id': 'mlbamID',
                        'xwoba': 'xwOBA',
                        'xba': 'xBA',
                        'xslg': 'xSLG',
                        'xiso': 'xISO',
                        'brl_percent': 'brl_pct',
                        'exit_velocity': 'exit_velo',
                    }
                )

"""
    Arguments: 
        data: string - string representing dict of rankings and values

    Returns: 
        defaultdict: {
            metric_name: {
                'rank',
                'value'
            }
        }
"""
def pair_ranks_with_data(data):
    season_ranks = defaultdict(dict)
    for k, v in data.items():
        k_splits = k.partition('_rank')
        metric, metric_type = k_splits[0], k_splits[1]
        metric_type = 'rank' if metric_type == '_rank' else 'value'

        season_ranks[metric][metric_type] = v
    return season_ranks


"""
    Min-Max Normalization

    Arguments:
        DataFrame

    Returns: DataFrame

"""

def min_max_normalize(df):
  return round((df-df.min())/(df.max()-df.min()), 3)

"""
    Helper Function for Strike Zone Normalization

    Arguments:
        DataFrame Row

    Returns:
        Float
"""

def avg_sz(row, avg_sz_height): 
    delta = (row['sz_top'] - row['sz_bot']) / avg_sz_height
    return round(row['plate_z'] * (2-delta), 2)

