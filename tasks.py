import requests
import time
import argparse
import csv
import json
import sqlite3

parser = argparse.ArgumentParser()
parser.add_argument('task', help="""
choose from: grouped-teams, players-stats, teams-stats""")
parser.add_argument("--name", required=False, help="""
choose first or last name of the player, used if task is grouped-teams""")
parser.add_argument("--season", required=False, help="""
choose season, used if task is teams-stats""")
parser.add_argument("--output", required=False, help="""
choose output method from: csv, json, sqlite, stdout (default).
 Used if task  is teams-stats""")
args = parser.parse_args()

if args.task not in ["grouped-teams", "players-stats", "teams-stats"]:
    print("""
invalid argument: {}, you need to provide one of the following:
 grouped-teams, players-stats, teams-stats
    """.format(args.task))
    exit()


def tryAgainIfError(code, http, par, cooldown, maxCooldown):
    data = requests.get(http, params=par)
    while data.status_code == code:
        time.sleep(cooldown)
        data = requests.get(http, params=par)
        cooldown = cooldown+10
        if cooldown > maxCooldown:
            break
    return data


if args.task == "grouped-teams":

    class Team:

        def __init__(
                self, name, abbrevation, division):
            self.name = name
            self.abbrevation = abbrevation
            self.division = division

    class Division:

        def __init__(self, name):
            self.name = name
            self.teams = []

        def addteam(self, team):
            self.teams.append(team)

        def printdata(self):
            print(self.name)
            for team in self.teams:
                print("    "+team.name+" ("+team.abbrevation+")")

    divs = {}
    currentPage = 0
    totalPages = 1
    while currentPage != totalPages and totalPages != 0:
        teamsData = tryAgainIfError(
            429, 'https://www.balldontlie.io/api/v1/teams',
            {'page': currentPage+1, 'per_page': 100}, 5, 200)
        teamsData = teamsData.json()
        for data in teamsData["data"]:
            if data['division'] not in divs.keys():
                divs[data['division']] = Division(data['division'])
            divs[data['division']].addteam(Team(data['full_name'],
                                                data['abbreviation'],
                                                divs[data['division']]))

        currentPage = teamsData["meta"]["current_page"]
        totalPages = teamsData["meta"]["total_pages"]

    for div in divs.values():
        div.printdata()

if args.task == "players-stats":

    class Player:
        def __init__(self, name, weight, height):
            self.name = name
            self.weight = weight
            self.height = height

    class Players:

        def __init__(self):
            self.list = []

        def add(self, player):
            self.list.append(player)

        def maxWeight(self):
            if self.list != []:
                return sorted(
                            self.list, key=lambda x: x.weight, reverse=True)[0]

        def maxHeight(self):
            if self.list != []:
                return sorted(
                            self.list, key=lambda x: x.height, reverse=True)[0]

    def feetToMeters(feet, inches):
        if feet is None or inches is None:
            return 0
        else:
            return (float(feet)*30.48 + float(inches)*2.54)/100

    def poundsToKg(pounds):
        if pounds is None:
            return 0
        else:
            return 0.453592*float(pounds)
    if args.name is not None:
        name = args.name
    else:
        print('You need to provide --name argument!')
        exit()

    players = Players()
    currentPage = 0
    totalPages = 1

    while currentPage != totalPages and totalPages != 0:
        playersData = tryAgainIfError(
            429, 'https://www.balldontlie.io/api/v1/players',
            {'page': currentPage + 1, 'per_page': 100, 'search': name}, 5, 200)
        playersData = playersData.json()
        for player in playersData["data"]:
            if player["first_name"] == name or player["last_name"] == name:
                players.add(
                    Player(player["first_name"] + " " + player["last_name"],
                           poundsToKg(player["weight_pounds"]),
                           feetToMeters(player["height_feet"],
                           player["height_inches"])))

        currentPage = playersData["meta"]["current_page"]
        totalPages = playersData["meta"]["total_pages"]
    if players.list == []:
        print("The tallest player: Not found")
        print("The heaviest player: Not found")
    else:
        if (players.maxHeight().height == 0):
            print("The tallest player: Not found")
        else:
            print(
                "The tallest player: " + players.maxHeight().name +
                " " + str(round(players.maxHeight().height, 2)) + " meters")

        if (players.maxWeight().weight == 0):
            print("The heaviest player: Not found")
        else:
            print(
                "The heaviest player: " + players.maxWeight().name +
                " " + str(round(players.maxWeight().weight, 2)) + " kilograms")

if args.task == "teams-stats":

    if args.output not in [None, "csv", "json", "sqlite", "stdout"]:
        print("invalid --output argument: " + args.output)
        exit()

    class Team:

        def __init__(self, name):
            self.name = name
            self.gamesWonAsHomeTeam = 0
            self.gamesLostAsHomeTeam = 0
            self.gamesWonAsVisitorTeam = 0
            self.gamesLostAsVisitorTeam = 0

        def addWin(self, homeOrVisitor):
            if homeOrVisitor == "home":
                self.gamesWonAsHomeTeam = self.gamesWonAsHomeTeam + 1
            if homeOrVisitor == "visitor":
                self.gamesWonAsVisitorTeam = self.gamesWonAsVisitorTeam + 1

        def addLose(self, homeOrVisitor):
            if homeOrVisitor == "home":
                self.gamesLostAsHomeTeam = self.gamesLostAsHomeTeam + 1
            if homeOrVisitor == "visitor":
                self.gamesLostAsVisitorTeam = self.gamesLostAsVisitorTeam + 1

        def stdout(self):
            print(self.name)
            print(
                "    won games as home team: " +
                str(self.gamesWonAsHomeTeam))
            print(
                "    won games as visitor team: " +
                str(self.gamesWonAsVisitorTeam))
            print(
                "    lost games as home team: " +
                str(self.gamesLostAsHomeTeam))
            print(
                "    lost games as visitor team: " +
                str(self.gamesLostAsVisitorTeam))

        def array(self):
            return [
                self.name, self.gamesWonAsHomeTeam,
                self.gamesWonAsVisitorTeam,
                self.gamesLostAsHomeTeam,
                self.gamesLostAsVisitorTeam]

        def dictionary(self):
            return {
                "team_name": self.name,
                "won_games_as_home_team": self.gamesWonAsHomeTeam,
                "won_games_as_visitor_team:": self.gamesWonAsVisitorTeam,
                "lost_games_as_home_team": self.gamesLostAsHomeTeam,
                "lost_games_as_visitor_team": self.gamesLostAsVisitorTeam}

    if args.season is not None:
        season = int(args.season)
    else:
        print("You need to provide --season argument!")
        exit()

    teams = {}
    currentPage = -1
    totalPages = 1

    while currentPage != totalPages and totalPages != 0:
        gamesData = tryAgainIfError(
            429, 'https://www.balldontlie.io/api/v1/games',
            {'page': currentPage + 1,
             'per_page': 100, 'seasons[]': season}, 5, 200)
        gamesData = gamesData.json()

        for game in gamesData["data"]:
            homeTeam = '{} ({})'.format(
                                game["home_team"]["full_name"],
                                game["home_team"]["abbreviation"])
            visitorTeam = '{} ({})'.format(
                                    game["visitor_team"]["full_name"],
                                    game["visitor_team"]["abbreviation"])

            if homeTeam not in teams.keys():
                teams[homeTeam] = Team(homeTeam)
            if visitorTeam not in teams.keys():
                teams[visitorTeam] = Team(visitorTeam)

            if game["home_team_score"] > game["visitor_team_score"]:
                teams[homeTeam].addWin("home")
                teams[visitorTeam].addLose("visitor")
            else:
                teams[visitorTeam].addWin("visitor")
                teams[homeTeam].addLose("home")

        currentPage = gamesData["meta"]["current_page"]
        totalPages = gamesData["meta"]["total_pages"]

    if teams == {}:
        print("no games found for " + args.season + " season")
    elif args.output is None or args.output == "stdout":
        for team in teams.values():
            team.stdout()
    elif args.output == "csv":
        arrays = [["Team name", "Won games as home team",
                                "Won games as visitor team",
                                "Lost games as home team",
                                "Lost games as visitor team"]]
        for team in teams.values():
            arrays.append(team.array())
        try:
            with open(
                'teams-stats_season_'+str(season)+'.csv',
                    'w', encoding='UTF-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(arrays)
        except Exception:
            print("failed to save the file")
            exit()
    elif args.output == "json":
        array = []
        for team in teams.values():
            array.append(team.dictionary())
        try:
            with open('teams-stats_season_{}.json'.format(
                                                    season), 'w') as outfile:
                json.dump(array, outfile)
        except Exception:
            print("failed to save the filme")
            exit()
    elif args.output == "sqlite":
        conn = sqlite3.connect('teams-stats_season_{}.sqlite'.format(
                                                    season))
        c = conn.cursor()
        try:
            c.execute('''CREATE TABLE team_stats
                (team_name TEXT, won_games_as_home_team INTEGER,
                won_games_as_visitor_team INTEGER,
                lost_games_as_home_team INTEGER,
                lost_games_as_visitor_team INTEGER)''')
        except Exception:
            print("""
database team_stats.sqlite already exists!
Delete or move it to another directory and try again.
                """)
        for team in teams.values():
            c.execute("""INSERT INTO team_stats VALUES
            (?, ?, ?, ?, ?)""", (
                                team.name,
                                team.gamesWonAsHomeTeam,
                                team.gamesWonAsVisitorTeam,
                                team.gamesLostAsHomeTeam,
                                team.gamesLostAsVisitorTeam))
        conn.commit()
