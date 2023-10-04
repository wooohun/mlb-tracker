import json
import pybaseball as pb
import pandas as pd
from pybaseball.lahman import *
from collections import defaultdict
from datetime import date, datetime
from utils import create_client, get_career_range, get_player_bio, get_player_ids
from pprint import pprint


STATCAST_VALID_DATES = {
	2008: (date(2008, 3, 25), date(2008, 10, 27)),
	2009: (date(2009, 4, 5), date(2009, 11, 4)),
	2010: (date(2010, 4, 4), date(2010, 11, 1)),
	2011: (date(2011, 3, 31), date(2011, 10, 28)),
	2012: (date(2012, 3, 28), date(2012, 10, 28)),
	2013: (date(2013, 3, 31), date(2013, 10, 30)),
	2014: (date(2014, 3, 22), date(2014, 10, 29)),
	2015: (date(2015, 4, 5), date(2015, 11, 1)),
	2016: (date(2016, 4, 3), date(2016, 11, 2)),
	2017: (date(2017, 4, 2), date(2017, 11, 1)),
	2018: (date(2018, 3, 29), date(2018, 10, 28)),
	2019: (date(2019, 3, 20), date(2019, 10, 30)),
	2020: (date(2020, 7, 23), date(2020, 10, 27)),
    2021: (date(2021, 4, 1), date(2021, 10, 3)),
    2022: (date(2022, 4, 7), date(2022, 10, 2)),
    2023: (date(2023, 3, 30), date.today())
}

POSITIONS = ['P', 'C', 'DH', '1B', '2B', '3B', 'SS', 'LF', 'RF', 'CF', 'OF']


def populate_player_collection():
    client = create_client()
    db = client.mlbDB
    players = db.playerProfiles.find({}, projection={'_id': 0})
    for player in players:
        statcast = add_statcast(player)
        if statcast: 
            db.playerProfiles.update_one({'id': player['id']}, {{'$set': {'statcast': statcast}}, {'$currentDate': {'updated': date.today()}}})

    
def add_statcast(player):
    seasons = player['seasons']
    mlbam_id = player['mlbamID']

    statcast = []
    for season in seasons:
        roles_by_year = season.keys()
        annual_data = {
            'year': season['year']
        }
        if 'hitting' in roles_by_year:
            query_values = get_batting_arsenal(season['year'], mlbam_id)
            if query_values:
                annual_data['hitting'] = {'pitch_types': query_values}
        if 'pitching' in roles_by_year:
            query_values = get_pitching_arsenal(season['year'], mlbam_id)
            if query_values:
                annual_data['pitching'] = {'pitch_types': query_values}
        statcast.append(annual_data)

    return statcast


# Statcast data on player performance vs pitches in a given year
def get_batting_arsenal(year, mlbam_id):
    sbpa = pb.statcast_batter_pitch_arsenal(year)
    if sbpa.empty:
        return None
    sbpa = sbpa.drop(
        columns=[
            'last_name, first_name',
        ]
    ).rename(
        columns={
            'player_id': 'mlbam_id', 
            'whiff_percent': 'whiff_pct', 
            'k_percent': 'k_pct',
            'hard_hit_percent': 'hard_hit_pct'
        }
    )

    # query df for player, add data to statcast['hitting']
    player_query = sbpa[sbpa['mlbam_id'] == mlbam_id]
    player_query = player_query.set_index('pitch_type')
    player_query = player_query.drop(columns=['mlbam_id'])
    query_json = player_query.to_json(orient='index')
    query_values = json.loads(query_json).items()
    res = {}
    for (key, val) in query_values:
        res[key] = val
    return res

# get metrics for pitches by year, pitcher
# shorten key names to reduce db storage required
def get_pitching_arsenal(year, mlbam_id):
    # Statcast Pitch Abbr: 
    pitches = {
        'FF': '4-Seamer', 
        'SIFT': 'Sinker', 
        'FC': 'Cutter', 
        'SL': 'Slider', 
        'CH': 'Changeup', 
        'CUKC': 'Curveball', 
        'FS': 'Splitter', 
        'KN': 'Knuckleball', 
        'ST': 'Sweeper', 
        'SV': 'Slurve'
    }
    res = defaultdict(dict)

    # grab data
    pitch_data = get_arsenal_data(year, mlbam_id)
    stats_values = get_pitching_arsenal_stats(year, mlbam_id)

    # Compile data into dict, key: pitch type abbr, value: metrics
    for k, v in pitch_data.items():
        seg = k.split('_', 1)
        front, back = seg[0].upper(), seg[1].upper()
        if front == 'CU':
            front = 'CUKC'
        elif front == 'SI':
            front = 'SIFT'
        elif back == 'CU':
            back == 'CUKC'
        elif back == 'SI':
            back = 'SIFT'
        if front in pitches:
            res[front].update({back: v})
        elif back in pitches:
            res[back].update({'usage_pct': v})

    for (p_type, p_data) in stats_values:
        for k, v in p_data.items():
            if k != 'player_id':
                p_key = p_type
                res[p_key].update({k: v})

    for key in res.keys():
        data = get_pitch_movement_data(year, mlbam_id, key)
        if data: 
            res[key].update({'movement': data})

    return res

def get_arsenal_data(year, mlbam_id):
    # query for all pitcher pitch arsenals by year
    sppa = pb.statcast_pitcher_pitch_arsenal(year)
    sppa.drop(
        columns=[
            'last_name, first_name',
        ])
    sppa_spin = sppa.merge(
        pb.statcast_pitcher_pitch_arsenal(year, arsenal_type='avg_spin'),
        left_on='pitcher',
        right_on='pitcher'
    )
    sppa_final = sppa_spin.rename(columns={'pitcher': 'mlbam_id'})

    # query gathered dataframes for player specific data
    # player_query = sppa_final.query(f'mlbam_id == {mlbam_id}')
    player_query = sppa_final[sppa_final['mlbam_id'] == mlbam_id]

    # verify that data exists
    if player_query.empty:
        return player_query
    player_query = player_query.drop(
            columns=['mlbam_id']
        ).dropna(axis='columns', how='all')
    pitch_json = player_query.to_json(orient='records')
    pitch_values = json.loads(pitch_json)[0]
    return pitch_values
    

def get_pitching_arsenal_stats(year, mlbam_id):
    # query for all pitcher pitch stats by year
    sppa_stats = pb.statcast_pitcher_arsenal_stats(year)

    # grab player specific stats
    stats_query = sppa_stats[sppa_stats['player_id'] == mlbam_id]
    # verify data exists
    if stats_query.empty:
        return []
    stats_query = stats_query.drop(columns=[
            'last_name, first_name', 
            'team_name_alt', 'pitch_name', 
            'player_id'
        ]).rename(columns={
        'pitches': 'total',
        'pitch_usage': 'usage',
        'whiff_percent': 'whiff_pct',
        'k_percent': 'k_pct',
        'hard_hit_percent': 'hard_hit_pct'
    })
    pitch_stats = stats_query.set_index('pitch_type')
    pitch_stats_json = pitch_stats.to_json(orient='index')
    stats_values = list(json.loads(pitch_stats_json).items())

    return stats_values

def get_pitch_movement_data(year, mlbam_id, pitch):
    movement_data = pb.statcast_pitcher_pitch_movement(
        year,
        pitch_type=pitch                    
    )
    # verify data exists
    if movement_data.empty:
        return None
    movement_data = movement_data[movement_data['pitcher_id'] == mlbam_id]
    # verify player specifc pitch data
    if movement_data.empty:
        return None
    
    movement_data = movement_data.drop(
        columns=[
            'year',
            'last_name, first_name',
            'pitcher_id',
            'team_name',
            'team_name_abbrev',
            'avg_speed',
            'pitches_thrown',
            'pitch_type_name',
            'pitch_hand',
            'total_pitches'
        ]
    )
    jsn = movement_data.set_index('pitch_type').to_json(orient='index')
    data = json.loads(jsn)

    return data[pitch]


"""
    Initial API call gives basic player info
    Use Pybaseball to get standard, advanced, batted-ball/pitch-level metrics


"""

def compile_player_data():
    # stick to small range, add more later
    # Statcast Range: 2008-present
    years = [2021, 2023]

    p_bios = people().dropna(axis='columns', how='all')

    # client = create_client()
    # db = client.mlbDB

    szn_b_data = pb.batting_stats(years[0], years[1], qual=50).dropna(axis='columns', how='all').sort_values(by='IDfg')
    szn_p_data = pb.pitching_stats(years[0], years[1], qual=50).dropna(axis='columns', how='all').sort_values(by='IDfg')

    tot_p_data = []
    prev = None

    # For seasons where pitchers recorded both hitting/pitching data
    for p_idx, player in szn_p_data.iterrows():
        if prev == player['Name']:
            continue
        prev = player['Name']

        p_bio = get_player_bio(p_bios, player['IDfg'], player['Name'])
        if p_bio is None:
            continue
        res = p_bio
        res['seasons'] = []

        player_bat_data = szn_b_data[szn_b_data['IDfg'] == player['IDfg']]
        player_pitch_data = szn_p_data[szn_p_data['IDfg'] == player['IDfg']]

        for s_idx, szn in player_pitch_data.iterrows():
            szn_p_data.drop(s_idx, inplace=True)
            
            std_pitch = szn['Team': 'SO']
            std_pitch['WHIP'] = szn['WHIP']
            std_pitch = std_pitch.to_json(orient='index')
            adv_pitch = szn['K/9': 'FIP'].to_json(orient='index')

            szn_data = {
                'year': szn['Season'],
                'pitching': {
                    'standard': std_pitch,
                    'advanced': adv_pitch
                }
            }

            if not player_bat_data.empty:
                target_szn_bat_data = player_bat_data[player_bat_data['Season'] == szn['Season']]
                if not target_szn_bat_data.empty:

                    bat_idx = target_szn_bat_data.index
                    szn_b_data.drop(bat_idx, inplace=True)

                    std_bat = target_szn_bat_data.loc[:, 'Team':'AVG'].to_json(orient='index')
                    bb = target_szn_bat_data.loc[:, 'GB': 'BUH%'].to_json(orient='index')
                    adv_bat = target_szn_bat_data.loc[:, 'wOBA': 'Clutch'].to_json(orient='index')

                    szn_data['batting'] = {
                        'standard': std_bat,
                        'batted_ball': bb,
                        'advanced': adv_bat
                    }

            res['seasons'].append(szn_data)
        tot_p_data.append(res)

    prev = None
    # Gather remainder of players who only hit
    for p_idx, player in szn_b_data.iterrows():

        if prev == player['Name']:
            continue
        prev = player['Name']

        p_bio = get_player_bio(p_bios, player['IDfg'], player['Name'])

        if p_bio is None:
            continue

        res = p_bio
        res['seasons'] = []

        player_hit_data = szn_b_data[szn_b_data['IDfg'] == player['IDfg']]

        for s_idx, szn in player_hit_data.iterrows():

            std_bat = szn['Team':'AVG'].to_json(orient='index')
            bb = szn['GB': 'BUH%'].to_json(orient='index')
            adv_bat = szn['wOBA': 'Clutch'].to_json(orient='index')

            szn_data = {
                'year': szn['Season'],
                'batting': {
                    'standard': std_bat,
                    'batted_ball': bb,
                    'advanced': adv_bat
                }
            }
            res['seasons'].append(szn_data)
        tot_p_data.append(res)

    return tot_p_data

    
# def get_season_batters(year):
#     data = pb.batting_stats(year, qual=50).dropna(axis='columns', how='all')
