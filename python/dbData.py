#!/usr/bin/python
import MySQLdb
import lib

def genQueryInsert(table_name, json_data):
    "function to insert values into a table"
    query = "INSERT INTO " + table_name + "("
    for key in json_data:
        query += key + ","
    query = query[:-1]
    query += ") VALUES ("
    for key in json_data:
        if type(json_data[key]) is bool:
            query += str(int(json_data[key])) + ","
        elif type(json_data[key]) is int:
            query += str(json_data[key]) + ","
        elif type(json_data[key]) is str or type(json_data[key]) is unicode:
            query += json_data[key] + ","
    query = query[:-1]
    query += ");"
    return query

def updateGame(gameId, win, opponent, debug=True):
    "function to the database with thje data of a game"

    # load database cretentials
    db_creds = lib.json_load('db.json', '../private/')
    user_lvl = 1 # only SELECT, INSERT, UPDATE

    # load match data
    match = lib.json_load(gameId + '_match.json')

    # Open database connection
    db = MySQLdb.connect(
        db_creds['host'],
        db_creds['users'][user_lvl]['name'],
        db_creds['users'][user_lvl]['password'],
        db_creds['name']
    )

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # add columns to games table
    match['win'] = win
    match['opposingTeamName'] = opponent
    query = genQueryInsert('games', match)
    if debug: print query
    else: cursor.execute(query)

    # disconnect from server
    db.close()
    return

updateGame(str(2117389806), True, 'Hanuele')
