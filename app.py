import os

import football, cricket

from flask import Flask, request, Response, redirect

app = Flask(__name__)


def sports():
	''' An enum for all the sports '''
	enums = dict(
    FOOTBALL="football",
    CRICKET="cricket",
    TENNIS="tennis"
	)
	
	return type('Enum', (), enums)

def scores():
	''' An enum for different type of match scores '''
	enums = dict(
    LIVE="live",
    LEAGUE="league",
    TEAM="team",
	)

	return type('Enum', (), enums)

def get_response_string(q):
	''' Returns the response string for a query '''
  q_data = q.json
  # check = ' :white_check_mark:' if q.json['is_answered'] else ''
  # return "|%d|%s <%s|%s> (%d answers)" % (q_data['score'], check, q.url,
  #                                         q.title, q_data['answer_count'])

def get_football_scores(type_score):
	''' Returns all the queries for football scores '''

	if type_score == scores().LIVE:
		football.get_live_football_scores()
	elif type_score == scores().LEAGUE:
		football.get_league_football_scores(league)
	elif team == scores().TEAM:
		football.get_team_football_scores(team)
	else:
		return 'Invalid argument. Please choose from ...'


def get_cricket_scores(type_score):
	''' Return results for all cricket scores '''
	pass



@app.route('/scores', methods=['post'])
def overflow():
  '''
  Example:
      /scores python list comprehension
  '''
  text = request.values.get('text')

  #TODO: define type_score
  if text == sports().FOOTBALL:
  	get_football_scores(type_score)
  elif text == sports().CRICKET:
  	get_cricket_scores(type_score)
  else:
  	return "Invalid sport. Please try `/scores football` or `/scores cricket`"

