# import click
# import csv
import datetime
import json
import io

import leagueids
import leagueproperties

from abc import ABCMeta, abstractmethod
from itertools import groupby
from collections import namedtuple

LEAGUE_PROPERTIES = leagueproperties.LEAGUE_PROPERTIES
LEAGUE_IDS = leagueids.LEAGUE_IDS


def get_writer(output_format='stdout', output_file=None):
    return globals()[output_format.capitalize()](output_file)


class BaseWriter(object):

    __metaclass__ = ABCMeta

    def __init__(self, output_file):
        self.output_filename = output_file

    @abstractmethod
    def live_scores(self, live_scores):
        pass

    @abstractmethod
    def team_scores(self, team_scores, time):
        pass

    @abstractmethod
    def team_players(self, team):
        pass

    @abstractmethod
    def standings(self, league_table, league):
        pass

    @abstractmethod
    def league_scores(self, total_data, time):
        pass

    def supported_leagues(self, total_data):
        """Filters out scores of unsupported leagues"""
        supported_leagues = {val: key for key, val in LEAGUE_IDS.items()}
        get_league_id = lambda x: int(x["_links"]["soccerseason"]["href"].split("/")[-1])
        fixtures = (fixture for fixture in total_data["fixtures"]
                    if get_league_id(fixture) in supported_leagues)

        # Sort the scores by league to make it easier to read
        fixtures = sorted(fixtures, key=get_league_id)
        for league, scores in groupby(fixtures, key=get_league_id):
            league = supported_leagues[league]
            for score in scores:
                yield league, score


class Stdout(BaseWriter):

    def __init__(self, output_file):
      self.Result = namedtuple("Result", "homeTeam, goalsHomeTeam, awayTeam, goalsAwayTeam")


    def live_scores(self, live_scores):
      """Prints the live scores in a pretty format"""
      scores = sorted(live_scores["games"], key=lambda x: x["league"])
      for league, games in groupby(scores, key=lambda x: x["league"]):
        self.league_header(league)
        for game in games:
          self.scores(self.parse_result(game), add_new_line=False)
          output += '   %s' % game["time"]

        output += '\n'
        return output

    # def team_scores(self, team_scores, time):
    #   """Prints the teams scores in a pretty format"""
    #   for score in team_scores["fixtures"]:
    #       if score["status"] == "FINISHED":
    #           click.echo()
    #           click.secho("%s\t" % score["date"].split('T')[0],
    #                       fg=self.colors.TIME, nl=False)
    #           self.scores(self.parse_result(score))

    # def team_players(self, team):
    #     """Prints the team players in a pretty format"""
    #     players = sorted(team['players'], key=lambda d: (d['jerseyNumber']))
    #     click.secho("%-4s %-25s    %-20s    %-20s    %-15s    %-10s" %
    #                 ("N.",  "NAME", "POSITION", "NATIONALITY", "BIRTHDAY", "MARKET VALUE"), bold=True, fg=self.colors.MISC)
    #     for player in players:
    #         click.echo()
    #         click.secho("%-4s %-25s    %-20s    %-20s    %-15s    %-10s" % 
    #                     (str(player["jerseyNumber"]), player["name"].encode('utf-8'), player["position"].encode('utf-8'), 
    #                         player["nationality"].encode('utf-8'), player["dateOfBirth"].encode('utf-8'), 
    #                         str(player["marketValue"].encode('utf-8'))), bold=True)


    def standings(self, league_table, league):
      """ Prints the league standings in a pretty way """
      output = "%-6s  %-30s    %-10s    %-10s    %-10s" %
                  ("POS", "CLUB", "PLAYED", "GOAL DIFF", "POINTS")
      output += '\n'
      positionlist = [team["position"] for team in league_table["standing"]]
      for team in league_table["standing"]:
        if team["goalDifference"] >= 0:
          team["goalDifference"] = ' ' + str(team["goalDifference"])
        
        output += "%-6s  %-30s    %-9s    %-11s    %-10s" %
            (str(team["position"]), team["teamName"],
             str(team["playedGames"]), team["goalDifference"], str(team["points"])
        # if LEAGUE_PROPERTIES[league]["cl"][0] <= team["position"] <= LEAGUE_PROPERTIES[league]["cl"][1]:
        #     click.secho("%-6s  %-30s    %-9s    %-11s    %-10s" %
        #                 (str(team["position"]), team["teamName"],
        #                  str(team["playedGames"]), team["goalDifference"], str(team["points"])),
        #                 bold=True, fg=self.colors.CL_POSITION)
        # elif LEAGUE_PROPERTIES[league]["el"][0] <= team["position"] <= LEAGUE_PROPERTIES[league]["el"][1]:
        #     click.secho("%-6s  %-30s    %-9s    %-11s    %-10s" %
        #                 (str(team["position"]), team["teamName"],
        #                  str(team["playedGames"]), team["goalDifference"], str(team["points"])),
        #                 fg=self.colors.EL_POSITION)
        # elif LEAGUE_PROPERTIES[league]["rl"][0] <= team["position"] <= LEAGUE_PROPERTIES[league]["rl"][1]:  # 5-15 in BL, 5-17 in others
        #     click.secho("%-6s  %-30s    %-9s    %-11s    %-10s" %
        #                 (str(team["position"]), team["teamName"],
        #                  str(team["playedGames"]), team["goalDifference"], str(team["points"])),
        #                 fg=self.colors.RL_POSITION)
        else:
          output += "%-6s  %-30s    %-9s    %-11s    %-10s" %
              (str(team["position"]), team["teamName"],
               str(team["playedGames"]), team["goalDifference"], str(team["points"]))

    def league_scores(self, total_data, time):
        """Prints the data in a pretty format"""
      seen = set()
      for league, data in self.supported_leagues(total_data):
        if league not in seen:
          seen.add(league)
          self.league_header(league)
        self.scores(self.parse_result(data))

    def league_header(self, league):
      """Prints the league header"""
      league_name = " {0} ".format(league)
      return "{:=^62}".format(league_name)

    def scores(self, result, add_new_line=True):
      """Prints out the scores in a pretty format"""
      # if result.goalsHomeTeam > result.goalsAwayTeam:
      #     homeColor, awayColor = (self.colors.WIN, self.colors.LOSE)
      # elif result.goalsHomeTeam < result.goalsAwayTeam:
      #     homeColor, awayColor = (self.colors.LOSE, self.colors.WIN)
      # else:
      #     homeColor = awayColor = self.colors.TIE

      click.secho('%-25s %2s' % (result.homeTeam, result.goalsHomeTeam),
                  bold=True, fg=homeColor, nl=False)
      click.secho("  vs ", nl=False)
      click.secho('%2s %s' % (result.goalsAwayTeam, result.awayTeam.rjust(25)),
                  fg=awayColor, nl=add_new_line)

    def parse_result(self, data):
      """Parses the results and returns a Result namedtuple"""
      def valid_score(score):
          return "-" if score == -1 else score

      if "result" in data:
        result = self.Result(
          data["homeTeamName"],
          valid_score(data["result"]["goalsHomeTeam"]),
          data["awayTeamName"],
          valid_score(data["result"]["goalsAwayTeam"]))
      else:
        result = self.Result(
          data["homeTeamName"],
          valid_score(data["goalsHomeTeam"]),
          data["awayTeamName"],
          valid_score(data["goalsAwayTeam"]))

      return result
