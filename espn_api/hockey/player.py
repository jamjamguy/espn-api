import pandas as pd

from espn_api.utils.utils import json_parsing
from .constant import POSITION_MAP, STATS_MAP, PRO_TEAM_MAP, STATS_IDENTIFIER


class Player(object):

    def __init__(self, data):
        self.name = json_parsing(data, 'fullName')
        self.playerId = json_parsing(data, 'id')
        self.position = POSITION_MAP[json_parsing(data, 'defaultPositionId') - 1]
        self.lineupSlot = POSITION_MAP.get(data.get('lineupSlotId'), '')
        self.eligibleSlots = [POSITION_MAP[pos] for pos in json_parsing(data, 'eligibleSlots')]
        self.acquisitionType = json_parsing(data, 'acquisitionType')
        self.proTeam = PRO_TEAM_MAP[json_parsing(data, 'proTeamId')]
        self.injuryStatus = json_parsing(data, 'injuryStatus')
        self.stats = {}
        self.df = {}

        '''
        Options
        1. Today
        2. This season (2021) 002021
        3. Last 7             012021
        4. Last 15            022021
        5. Last 30            032021
        6. Last season (2020) 002020
        7. 2021 Projections   102021
        '''
        player = data['playerPoolEntry']['player'] if 'playerPoolEntry' in data else data['player']
        self.injuryStatus = player.get('injuryStatus', self.injuryStatus)
        self.injured = player.get('injured', False)

        for split in player.get('stats', []):
            if split['stats']:
                id = split['id']
                stat_key = get_stat_key(id)

                self.stats[stat_key] = {}

                if 'stats' in split.keys():
                    self.stats[stat_key]['total'] = {STATS_MAP[i]: split['stats'][i] for i in split['stats'].keys()
                                                        if STATS_MAP[i] != ''}
                else:
                    self.stats[stat_key]['total'] = None

    def __repr__(self):
        return 'Player(%s)' % (self.name,)

    def to_df(self, stat: str) -> pd.DataFrame:
        if stat not in self.df:
            self.df[stat] = pd.DataFrame(self.stats[stat]['total'], index= [self.name])

        self.df[stat]['Team'] = [self.proTeam]
        self.df[stat]['Position'] = [self.position]
        self.df[stat]['lineUpSlot'] = [self.lineupSlot]

        return self.df[stat]

def get_stat_key(id: str) -> str:
    if id[:2] in STATS_IDENTIFIER:
        stat_type = STATS_IDENTIFIER[id[:2]]
        return stat_type + ' ' + id[2:]

    return id
