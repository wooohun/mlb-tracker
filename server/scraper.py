import json
import pybaseball as pb
import pandas as pd
from pybaseball.lahman import *
from collections import defaultdict
from datetime import date, datetime
from utils import get_player_bio, pair_ranks_with_data, min_max_normalize, avg_sz
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
    2023: (date(2023, 3, 30), date(2023, 10, 1))
}

POSITIONS = ['P', 'C', 'DH', '1B', '2B', '3B', 'SS', 'LF', 'RF', 'CF', 'OF']

def add_statcast(player):
    seasons = player['seasons']
    mlbam_id = player['mlbamID']

    statcast = []
    for idx, season in enumerate(seasons):
        roles_by_year = season.keys()
        annual_data = {
            'year': season['year']
        }

        if 'batting' in roles_by_year:
            query_values = get_batting_arsenal(season['year'], mlbam_id)
            if query_values:
                annual_data['batting'] = {'pitch_types': query_values}
        if 'pitching' in roles_by_year:
            query_values = get_pitching_arsenal(season['year'], mlbam_id)
            if query_values:
                annual_data['pitching'] = {'pitch_types': query_values}
            if 'pitching' in player['ranking'][idx].keys():
                if 'FF' in query_values.keys():
                    
                    player['ranking'][idx]['pitching']['fb_speed'] = {
                        'rank': player['ranking'][idx]['pitching']['fb_speed']['value'],
                        'value': query_values['FF']['AVG_SPEED']
                    }
                    player['ranking'][idx]['pitching']['fb_spin'] = {
                        'rank': player['ranking'][idx]['pitching']['fb_spin']['value'],
                        'value': query_values['FF']['AVG_SPIN']
                    }
        
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
            'team_name_alt',
            'pitch_name'
        ]
    ).rename(
        columns={
            'player_id': 'mlbam_id',
            'pitches': 'total', 
            'pitch_usage': 'usage',
            'whiff_percent': 'whiff_pct', 
            'k_percent': 'k_pct',
            'hard_hit_percent': 'hard_hit_pct',
            'est_ba': 'xBA',
            'est_slg': 'xSLG',
            'est_woba': 'xwOBA'
        }
    )

    # query df for player, add data to statcast['hitting']
    player_query = sbpa[sbpa['mlbam_id'] == mlbam_id]
    player_query = player_query.set_index('pitch_type')
    player_query = player_query.drop(columns=['mlbam_id'])
    query_json = player_query.to_json(orient='index')
    query_values = json.loads(query_json).items()
    
    # add normalized data values
    normalized = min_max_normalize(sbpa.loc[:, 'run_value_per_100': ])
    normalized = sbpa[['mlbam_id', 'pitch_type']].join(normalized, how='outer')
    norm_query = normalized[normalized['mlbam_id'] == mlbam_id].drop(columns=['mlbam_id'])
    norm_json = norm_query.set_index('pitch_type').to_json(orient='index')
    norm_values = json.loads(norm_json)

    res = {}
    for (key, val) in query_values:
        res[key] = val
        res[key].update({'normalized': norm_values[key]})
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
    stats_values, normalized = get_pitching_arsenal_stats(year, mlbam_id)

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
        res[p_type].update({'normalized': normalized[p_type]})
        for k, v in p_data.items():
            res[p_type].update({k: v})

    to_pop = []
    for key in res.keys():
        data = get_pitch_movement_data(year, mlbam_id, key)
        if data: 
            res[key].update({'movement': data})
        else:
            to_pop.append(key)
    for key in to_pop:
        res.pop(key)
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
        'hard_hit_percent': 'hard_hit_pct',
        'est_ba': 'xBA',
        'est_slg': 'xSLG',
        'est_woba': 'xwOBA'
    })

    norm_stats = sppa_stats.drop(columns=[
            'last_name, first_name', 
            'team_name_alt', 'pitch_name', 
        ]).rename(columns={
        'pitches': 'total',
        'pitch_usage': 'usage',
        'whiff_percent': 'whiff_pct',
        'k_percent': 'k_pct',
        'hard_hit_percent': 'hard_hit_pct',
        'est_ba': 'xBA',
        'est_slg': 'xSLG',
        'est_woba': 'xwOBA'
    })

    normalized = min_max_normalize(norm_stats.loc[:, 'run_value_per_100': ])
    normalized = sppa_stats[['player_id', 'pitch_type']].join(normalized, how='outer')
    norm_query = normalized[normalized['player_id'] == mlbam_id].drop(columns=['player_id'])
    norm_stats = norm_query.set_index('pitch_type')
    norm_json = norm_stats.to_json(orient='index')
    norm_values = json.loads(norm_json)

    pitch_stats = stats_query.set_index('pitch_type')
    pitch_stats_json = pitch_stats.to_json(orient='index')
    stats_values = list(json.loads(pitch_stats_json).items())

    return stats_values, norm_values

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

    szn_b_data = pb.batting_stats(years[0], years[1], qual=50).dropna(axis='columns', how='all').sort_values(by='IDfg')
    szn_p_data = pb.pitching_stats(years[0], years[1], qual=50).dropna(axis='columns', how='all').sort_values(by='IDfg')

    bat_rankings = get_batter_ranks(years)
    pitch_rankings = get_pitcher_ranks(years)

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
        res['averages'] = {}
        res['ranking'] = []

        player_bat_data = szn_b_data[szn_b_data['IDfg'] == player['IDfg']]
        player_pitch_data = szn_p_data[szn_p_data['IDfg'] == player['IDfg']]

        
        for s_idx, szn in player_pitch_data.iterrows():
            season_ranks = {
                'year': szn['Season']
            }
            player_pitch_ranks =  pitch_rankings.loc[(pitch_rankings['mlbamID'] == p_bio['mlbamID']) & (pitch_rankings['year'] == szn['Season'])]
            if not player_pitch_ranks.empty:
                ranking_data = szn.loc[
                    ['Name','Barrel%', 'HardHit%', 'EV', 'K%', 'BB%']
                ].rename({
                    'Name': 'player_name',
                    'Barrel%': 'brl_pct',
                    'HardHit%': 'hard_hit_pct',
                    'K%': 'k_pct',
                    'BB%': 'bb_pct'
                })
                ranking_data = ranking_data.to_frame().transpose()
                merged = player_pitch_ranks.merge(
                    ranking_data,
                    on='player_name',
                    suffixes=('_rank', None)
                )

                if not merged.empty:

                    jsn = merged.loc[:, 'xBA_rank': ].to_json(orient='index')
                    final = list(json.loads(jsn).values())[0]

                    pitch_ranks = pair_ranks_with_data(final)
                    season_ranks['pitching'] = pitch_ranks
            
            szn_p_data.drop(s_idx, inplace=True)
            
            std_pitch = szn['Team': 'SO']
            std_pitch['WHIP'] = szn['WHIP']
            std_pitch = std_pitch.to_json(orient='index')

            adv_pitch = szn['K/9': 'FIP']
            adv_pitch['brl_pct'] = szn['Barrel%']
            adv_pitch['hard_hit_pct'] = szn['HardHit%']
            adv_pitch = adv_pitch.to_json(orient='index')
            
            std_pitch = json.loads(std_pitch)
            adv_pitch = json.loads(adv_pitch)

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

                    player_bat_ranks = bat_rankings.loc[(bat_rankings['mlbamID'] == p_bio['mlbamID']) & (bat_rankings['year'] == szn['Season'])]
                    if not player_bat_ranks.empty:
                        ranking_data = target_szn_bat_data.loc[:, 
                            ['Name','Barrel%', 'HardHit%', 'EV', 'K%', 'BB%']
                        ].rename(columns={
                            'Name': 'player_name',
                            'Barrel%': 'brl_pct',
                            'HardHit%': 'hard_hit_pct',
                            'K%': 'k_pct',
                            'BB%': 'bb_pct'
                        })
                        merged = player_bat_ranks.merge(
                            ranking_data,
                            on='player_name',
                            suffixes=('_rank', None)
                        )
                        jsn = player_bat_ranks.loc[:, 'xwOBA_rank': ].to_json(orient='index')
                        ranking_data = list(json.loads(jsn).values())[0]
                        
                        bat_ranks = pair_ranks_with_data(ranking_data)
                        season_ranks['batting'] = bat_ranks

                    # get index of player batting data, drop
                    bat_idx = target_szn_bat_data.index
                    szn_b_data.drop(bat_idx, inplace=True)

                    std_bat = target_szn_bat_data.loc[:, 'Team':'AVG']
                    std_bat['OBP'] = target_szn_bat_data['OBP']
                    std_bat['SLG'] = target_szn_bat_data['SLG']
                    std_bat['OPS'] = target_szn_bat_data['OPS']
                    
                    adv_bat = target_szn_bat_data.loc[:, 'wOBA': 'Clutch']
                    adv_bat['brl_pct'] = target_szn_bat_data['Barrel%']
                    adv_bat['hard_hit_pct'] = target_szn_bat_data['HardHit%']
                    adv_bat['exit_velo'] = target_szn_bat_data['EV']
                    adv_bat['chase_pct'] = target_szn_bat_data['O-Swing%']
                    
                    std_bat = std_bat.to_json(orient='index')
                    bb = target_szn_bat_data.loc[:, 'GB': 'BUH%'].to_json(orient='index')
                    adv_bat = adv_bat.to_json(orient='index')

                    std_bat = list(json.loads(std_bat).values())[0]
                    bb = list(json.loads(bb).values())[0]
                    adv_bat = list(json.loads(adv_bat).values())[0]

                    szn_data['batting'] = {
                        'standard': std_bat,
                        'batted_ball': bb, 
                        'advanced': adv_bat
                    }
            res['seasons'].append(szn_data)
            res['ranking'].append(season_ranks)
        if not player_pitch_data.empty:
            agg = {}
            for k in player_pitch_data.loc[:, 'W':'BABIP'].keys():
                # sum up np.int64 dtype metrics
                if player_pitch_data[k].dtypes == '<i8':
                    agg[k] = player_pitch_data[k].sum().item()
                # find average of np.float64 dtype metrics
                elif player_pitch_data[k].dtypes == '<f8':
                    agg[k] = round(player_pitch_data[k].mean(), 3).item()
            res['averages']['pitching'] = agg
        if not player_bat_data.empty:
            agg = {}
            for k in player_bat_data.loc[:, 'G': 'OPS'].keys():
                if player_bat_data[k].dtypes == '<i8':
                    agg[k] = player_bat_data[k].sum().item()
                # find average of np.float64 dtype metrics
                elif player_bat_data[k].dtypes == '<f8':
                    agg[k] = round(player_bat_data[k].mean(), 3).item()
            res['averages']['batting'] = agg
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
        res['averages'] = {}
        res['ranking'] = []

        player_bat_data = szn_b_data[szn_b_data['IDfg'] == player['IDfg']]

        for s_idx, szn in player_bat_data.iterrows():
            player_bat_ranks = bat_rankings.loc[(bat_rankings['mlbamID'] == p_bio['mlbamID']) & (bat_rankings['year'] == szn['Season'])]
            if not player_bat_ranks.empty:

                ranking_data = szn.loc[
                    ['Name','Barrel%', 'HardHit%', 'EV', 'K%', 'BB%']
                ].rename({
                    'Name': 'player_name',
                    'Barrel%': 'brl_pct',
                    'HardHit%': 'hard_hit_pct',
                    'K%': 'k_pct',
                    'BB%': 'bb_pct'
                })
                ranking_data = ranking_data.to_frame().transpose()
                merged = player_bat_ranks.merge(
                    ranking_data,
                    on='player_name',
                    suffixes=('_rank', None)
                )

                if not merged.empty:
                    jsn = player_bat_ranks.loc[:, 'xwOBA_rank': ].to_json(orient='index')
                    ranking_data = list(json.loads(jsn).values())[0]
                            
                    bat_ranks = pair_ranks_with_data(ranking_data)
                    season_ranks = {
                        'year': szn['Season'],
                        'batting': bat_ranks
                    }
                    res['ranking'].append(season_ranks)

            std_bat = szn['Team':'AVG']
            std_bat['OBP'] = szn['OBP']
            std_bat['SLG'] = szn['SLG']
            std_bat['OPS'] = szn['OPS']

            adv_bat = szn['wOBA': 'Clutch']
            adv_bat['brl_pct'] = szn['Barrel%']
            adv_bat['hard_hit_pct'] = szn['HardHit%']
            adv_bat['exit_velo'] = szn['EV']
            adv_bat['chase_pct'] = szn['O-Swing%']
            
            std_bat = std_bat.to_json(orient='index')
            bb = szn['GB': 'BUH%'].to_json(orient='index')
            adv_bat = adv_bat.to_json(orient='index')

            std_bat = json.loads(std_bat)
            bb = json.loads(bb)
            adv_bat = json.loads(adv_bat)

            szn_data = {
                'year': szn['Season'],
                'batting': {
                    'standard': std_bat,
                    'batted_ball': bb,
                    'advanced': adv_bat
                }
            }
            res['seasons'].append(szn_data)
        agg = {}
        for k in player_bat_data.loc[:, 'G': 'OPS'].keys():
            if player_bat_data[k].dtypes == '<i8':
                agg[k] = player_bat_data[k].sum().item()
            # find average of np.float64 dtype metrics
            elif player_bat_data[k].dtypes == '<f8':
                agg[k] = round(player_bat_data[k].mean(), 3).item()
        res['averages']['batting'] = agg
        
        tot_p_data.append(res)

    return tot_p_data

"""
    Grab Batter Percentile Rankings for set range
    
    Returns: 
        DataFrame
"""

def get_batter_ranks(years):

    res = pd.DataFrame()
    for year in range(years[0], years[1]+1):
        df = pb.statcast_batter_percentile_ranks(year).dropna(
            axis='rows',
            how='all'
        ).drop(columns=[
            'xiso',
            'xobp',
            'whiff_percent',
            'oaa',
            'brl',
        ])
        qual_ranks = df[~df.isnull().any(axis=1)].rename(columns={
            'player_id': 'mlbamID',
            'xwoba': 'xwOBA',
            'xba': 'xBA',
            'xslg': 'xSLG',
            'exit_velocity': 'EV',
            'brl_percent': 'brl_pct',
            'k_percent': 'k_pct',
            'hard_hit_percent': 'hard_hit_pct',
            'bb_percent': 'bb_pct',
        })
        qual_bats = pb.statcast_batter_expected_stats(year).rename(columns={
            'player_id': 'mlbamID',
            'est_ba': 'xBA',
            'est_slg': 'xSLG',
            'est_woba': 'xwOBA'
        })
        qual_bats = qual_bats.loc[:, ['mlbamID', 'xBA', 'xSLG', 'xwOBA']]
        spd = pb.statcast_sprint_speed(year).rename(columns={'player_id': 'mlbamID'}).loc[:, ['mlbamID', 'sprint_speed']]
        merged = qual_ranks.merge(
            qual_bats,
            left_on='mlbamID',
            right_on='mlbamID',
            suffixes=('_rank', None)
        ).merge(
            spd,
            left_on='mlbamID',
            right_on='mlbamID',
            suffixes=('_rank', None)
        )
        res = pd.concat([res, merged])
    return res

"""
    Grab Pitcher Percentile Rankings for set range
    
    Returns: 
        DataFrame
"""

def get_pitcher_ranks(years):
    res = pd.DataFrame()
    for year in range(years[0], years[1]+1):
        df = pb.statcast_pitcher_percentile_ranks(year).dropna(
            axis='rows',
            how='all'
        ).drop(columns=[
            'xwoba',
            'xiso',
            'xobp',
            'brl',
            'curve_spin',
            'whiff_percent',
            'xslg'
        ])
        qual_ranks = df[~df.isnull().any(axis=1)].rename(
            columns={
                'player_id': 'mlbamID',
                'xba': 'xBA',
                'brl_percent': 'brl_pct',
                'exit_velocity': 'EV',
                'hard_hit_percent': 'hard_hit_pct',
                'k_percent': 'k_pct',
                'bb_percent': 'bb_pct',
                'xera': 'xERA',
                'fb_velocity': 'fb_speed',
            }
        )
        qual_pitch = pb.statcast_pitcher_expected_stats(2021).rename(columns={
            'player_id': 'mlbamID',
            'est_ba': 'xBA',
            'xera': 'xERA'
        })
        qual_pitches = qual_pitch.loc[:, ['mlbamID', 'xBA', 'xERA']]
        merged = qual_ranks.merge(
            qual_pitches,
            left_on='mlbamID',
            right_on='mlbamID',
            suffixes=('_rank', None)
        )
        res = pd.concat([res, merged])
    return res

def get_pitcher_pitches(season, mlbamid):
    start, end = STATCAST_VALID_DATES[season]
    start = start.strftime('%Y-%m-%d')
    end = end.strftime('%Y-%m-%d')

    data = pb.statcast_pitcher(start, end, mlbamid)
    if data.empty:
        return None
    data = data.sort_values(by='pitch_type')
    data = data.loc[:, ['pitch_type', 'zone', 'plate_x', 'plate_z', 'sz_top', 'sz_bot']]

    width = data.sort_values(by='plate_x')
    width = width.loc[width['zone'] < 10]

    szt = round(data['sz_top'].mean(), 2)
    szb = round(data['sz_bot'].mean(), 2)
    szl = round(width['plate_x'].min(), 2)
    szr = round(width['plate_x'].max(), 2)
    
    data.drop(columns=['zone'], inplace=True)
    sum_of_differences =  data.apply(lambda row: row['sz_top'] - row['sz_bot'], axis=1).sum()
    avg_sz_height = round(sum_of_differences/ len(data), 2).item()

    data['plate_z'] = data.apply(avg_sz, args=(avg_sz_height,), axis=1)

    data.drop(columns=['sz_top', 'sz_bot'], inplace=True)
    data = data.loc[data['pitch_type'].notna()]

    jsn = data.to_json(orient='records')
    pitches = json.loads(jsn)

    p_types = defaultdict(list)
    for pitch in pitches:
        coords = {
            'x': pitch['plate_x'],
            'y': pitch['plate_z']
        }
        p_types[pitch['pitch_type']].append(coords)
    
    res = {
        'sz_dim': {
            'top': szt,
            'bot': szb,
            'left': szl,
            'right': szr
        },
        'pitch_types': p_types
    }
    return res

def get_batter_pitches(season, mlbamid):
    start, end = STATCAST_VALID_DATES[season]
    start = start.strftime('%Y-%m-%d')
    end = end.strftime('%Y-%m-%d')

    data = pb.statcast_batter(start, end, mlbamid)
    if data.empty:
        return None
    
    data = data.sort_values(by='pitch_type')
    data = data.loc[:, ['pitch_type', 'zone', 'plate_x', 'plate_z', 'sz_top', 'sz_bot']]
    
    width = data.sort_values(by='plate_x')
    width = width.loc[width['zone'] < 10]

    szt = round(data['sz_top'].mean(), 2)
    szb = round(data['sz_bot'].mean(), 2)
    szl = round(width['plate_x'].min(), 2)
    szr = round(width['plate_x'].max(), 2)

    data.drop(columns=['zone'], inplace=True)
    sum_of_differences =  data.apply(lambda row: row['sz_top'] - row['sz_bot'], axis=1).sum()
    avg_sz_height = round(sum_of_differences/ len(data), 2).item()

    data['plate_z'] = data.apply(avg_sz, args=(avg_sz_height, ), axis=1)

    data.drop(columns=['sz_top', 'sz_bot'], inplace=True)
    data = data.loc[data['pitch_type'].notna()]

    jsn = data.to_json(orient='records')
    pitches = json.loads(jsn)

    p_types = defaultdict(list)
    for pitch in pitches:
        coords = {
            'x': pitch['plate_x'],
            'y': pitch['plate_z']
        }
        p_types[pitch['pitch_type']].append(coords)
    
    res = {
        'sz_dim': {
            'top': szt,
            'bot': szb,
            'left': szl,
            'right': szr
        },
        'pitch_types': p_types
    }
    return res