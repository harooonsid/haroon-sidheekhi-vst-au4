# -*- coding: utf-8 -*-
"""
Created on Sat Sep 17 20:05:38 2022

@author: dev
"""

import matplotlib.pyplot as plt
from mplsoccer import Pitch, Sbopen
import pandas as pd
parser = Sbopen()

import json
from pandas import json_normalize

with open('E:\SoccermaticsForPython-master\statsbomb\data\competitions.json') as d1:
    competitions = json.load(d1)
    
competition_id=72
season_id=30
with open('E:/SoccermaticsForPython-master/statsbomb/data/matches/'+str(competition_id)+'/'+str(season_id)+'.json') as d2:
    matches = json.load(d2)    
df_match = json_normalize(matches, sep = "_")

#finding out the list of match id's
team = "England Women's"
match_ids = df_match.loc[(df_match["home_team_home_team_name"] == team) | (df_match["away_team_away_team_name"] == team)]["match_id"].tolist()
no_games = len(match_ids)

danger_passes = pd.DataFrame()
for idx in match_ids:
    #open the event data from this game
    df = parser.event(idx)[0]
    for period in [1, 2]:
        #keep only accurate passes by England that were not set pieces in this period
        mask_pass = (df.team_name == team) & (df.type_name == "Pass") & (df.outcome_name.isnull()) & (df.period == period) & (df.sub_type_name.isnull())
        #keep only necessary columns
        passes = df.loc[mask_pass, ["x", "y", "end_x", "end_y", "minute", "second", "player_name"]]
        #keep only Shots by England in this period
        mask_shot = (df.team_name == team) & (df.type_name == "Shot") & (df.period == period)
        #keep only necessary columns
        shots = df.loc[mask_shot, ["minute", "second"]]
        #convert time to seconds
        shot_times = shots['minute']*60+shots['second']
        shot_window = 15
        #find starts of the window
        shot_start = shot_times - shot_window
        #condition to avoid negative shot starts
        shot_start = shot_start.apply(lambda i: i if i>0 else (period-1)*45)
        #convert to seconds
        pass_times = passes['minute']*60+passes['second']
        #check if pass is in any of the windows for this half
        pass_to_shot = pass_times.apply(lambda x: True in ((shot_start < x) & (x < shot_times)).unique())

        #keep only danger passes
        danger_passes_period = passes.loc[pass_to_shot]
        #concatenate dataframe with a previous one to keep danger passes from the whole tournament
        danger_passes = pd.concat([danger_passes, danger_passes_period])
        
#keep only surnames
danger_passes["player_name"] = danger_passes["player_name"].apply(lambda x: str(x).split()[-1])
#count passes by player and normalize them
pass_count = danger_passes.groupby(["player_name"]).x.count()/no_games
#make a histogram
ax = pass_count.plot.bar(pass_count)
#make legend
ax.set_xlabel("")
ax.set_ylabel("Number of danger passes per game")
plt.show()
