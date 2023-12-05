from datetime import datetime, timedelta
import json
import pytz
from nba_api.live.nba.endpoints import boxscore
from nba_api.stats.endpoints import Scoreboard
from nba_api.stats.library.parameters import LeagueID
from flask import Flask
import requests

def get_game_ids(day_offset=-1):
    gamefinder = Scoreboard(
        league_id=LeagueID.nba, day_offset=day_offset, game_date=datetime.now()
    )

    games_dict = gamefinder.get_normalized_dict()
    games = []
    for game in games_dict["GameHeader"]:
        games.append(game["GAME_ID"])

    return games

def get_tomorrows_game_ids():
    tomorrow = datetime.now() + timedelta(days=1)

    tomorrow = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)

    try:
        gamefinder = Scoreboard(
            league_id=LeagueID.nba, day_offset=0, game_date=tomorrow, timeout=30
        )
        games_dict = gamefinder.get_normalized_dict()
        games = [game["GAME_ID"] for game in games_dict["GameHeader"]]
    except requests.exceptions.Timeout as e:
        print(f"Timeout while fetching game data: {e}")
        games = []

    return games

def getlogo(teamid):
    path = f"https://cdn.nba.com/logos/nba/{teamid}/global/D/logo.svg"
    return path

def process_game_data(game_id):
    try:
        box = boxscore.BoxScore(game_id)
        timegetter = box.get_dict()
        game = timegetter['game']
        gametime = game['gameTimeUTC']

        game_time_utc_str = gametime
        game_time_utc = datetime.strptime(game_time_utc_str, '%Y-%m-%dT%H:%M:%SZ')

        poland_timezone = pytz.timezone('Europe/Warsaw')
        game_time_poland = game_time_utc.replace(tzinfo=pytz.utc).astimezone(poland_timezone)

        date_poland = game_time_poland.strftime('%Y-%m-%d')
        time_poland = game_time_poland.strftime('%H:%M:%S')

        team_away = box.away_team_stats.get_dict()
        team_home = box.home_team_stats.get_dict()
        away_logo = getlogo(team_away['teamId'])
        home_logo = getlogo(team_home['teamId'])
        score_away = team_away['teamName'], team_away['score'], away_logo
        score_home = team_home['teamName'], team_home['score'], home_logo
        score = {
            'date': date_poland,
            'time': time_poland,
            'away_team': score_away[0],
            'away_score': score_away[1],
            'away_logo': away_logo,
            'home_team': score_home[0],
            'home_score': score_home[1],
            'home_logo': home_logo,
        }

        def get_player_stats(players):
            stats = []
            for player in players:
                player_stats = {
                    'number': player['jerseyNum'],
                    'name': player['name'],
                    'position': player.get('position', 'N/A'),
                    'points': player['statistics']['points'],
                    'rebounds': player['statistics']['reboundsTotal'],
                    'assists': player['statistics']['assists'],
                    'blocks': player['statistics']['blocks'],
                    'fgp': f"{round(player['statistics']['fieldGoalsPercentage'] * 100, 2)}%",
                    'fouls': player['statistics']['foulsPersonal'],
                    'turnovers': player['statistics']['turnovers'],
                    'minutes': str(timedelta(minutes=float(player['statistics']['minutes'].split('M')[1].split('S')[0])))
                }
                stats.append(player_stats)

            return stats

        away_stats = get_player_stats(box.away_team.get_dict()['players'])
        home_stats = get_player_stats(box.home_team.get_dict()['players'])

        game_data = {
            'score': score,
            'away_stats': away_stats,
            'home_stats': home_stats
        }

        return game_data

    except json.decoder.JSONDecodeError as e:
        print(f"Error processing data for game {game_id}: {e}")
        return None
    except Exception as e:
        print(f"Error processing data for game {game_id}: {e}")
        return None

app = Flask(__name__)

@app.route('/')
def give_stats():
    all_game_data = {}

    for i, game_id in enumerate(get_game_ids(), start=1):
        game_data = process_game_data(game_id)
        if game_data:
            all_game_data[f'game{i}'] = game_data

    json_output = json.dumps(all_game_data, indent=2)

    return json_output

@app.route('/next_games')
def next_games():
    next_games_data = get_tomorrows_game_ids()
    return json.dumps(next_games_data, indent=2)

if __name__ == '__main__':
    app.run(debug=True)
