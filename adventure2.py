#! /usr/bin/python3
import threading
import time
import queue
import collections
import json
import os
import hashlib
import sys
import redis
import asyncio
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room




r = redis.Redis(host='192.168.1.246', port=6379, db=0)
def rset(key,value):
    r.set(key, json.dumps(value))

def rget(key):
    return json.loads(r.get(key))

#parties = []    
#invites = []
#clients = []
#games = []
#clientDict = {}
from multiprocessing import Process
app = Flask(__name__)
sio = SocketIO(app,async_mode = 'threading')



"""
def handleEvent(event,adventure,id):
    games = rget("games")
    thisgame = None
    i=0
    for game in games:
        if game["id"] == id:
            thisgame = i
            break
        i+=1
    if event["type"] == "say":
        sio.emit("gmSay",json.dumps(event),room=id)
    elif event["type"] == "script":
        sio.emit("gmScript",json.dumps(event),room=id)
    elif event["type"] == "MonsterCombat":
        games[thisgame]["combat"] = True
        sio.emit("startCombat",json.dumps(event),room=id)
    rset("games", games)
    print(event["type"])


@sio.on("startingGame")
def startingGame(data):
    data = json.loads(str(data))
    games = rget("games")
    i=0
    thisgame = None
    for game in games:
        if game["id"] == data["id"]:
            games[i]["advid"] = data["advid"]
            thisgame = game
        i+=1
    rset("games",games)
    print(thisgame)
    refs = json.load(open("adventures/ref.json","r"))
    advfile = ""
    for ref in refs:
        if ref["id"] == data["advid"]:
            advfile = ref["file"]
    print(advfile)
    advfile = json.load(open(advfile,"r"))
    for event in advfile["events"]:
        if event["id"] == advfile["initEvt"]:
            print("Handling")
            handleEvent(event,advfile,data["id"])


@sio.on("runEvent")
def runEvent(data):
    data = json.loads(str(data))
    games = rget("games")
    i=0
    thisgame = None
    for game in games:
        if game["id"] == data["gid"]:
            thisgame = game
        i+=1
    refs = json.load(open("adventures/ref.json","r"))
    advfile = ""
    for ref in refs:
        if ref["id"] == thisgame["advid"]:
            advfile = ref["file"]
    print(refs)
    advfile = json.load(open(advfile,"r"))
    for event in advfile["events"]:
        if event["id"] == data["eventID"]:
            print("Handling")
            handleEvent(event,advfile,data["gid"])

"""


# Handler for starting game
@sio.on("startingGame")
def startingGame(data):
    # Load data
    data = json.loads(str(data))

    # Get list of "games" from redis server
    games = rget("games")

    # Set "i" to zero
    i=0

    # Set "thisgame" to None
    thisgame = None

    # Loop through list of games
    for game in games:

        # If the games ID == the ID in data
        if game["id"] == data["id"]:
            # Set the games Adventure ID to the Adventure ID specified in data
            games[i]["advid"] = data["advid"]

            # Set "thisgame" to the game
            thisgame = game
        i+=1

    # Update "games" in redis to new values
    rset("games",games)

    # Print the contents of this game (debugging only)
    print(thisgame)

    # Set "refs" to the JSON contents of the adventure references file
    refs = json.load(open("adventures/ref.json","r"))

    # Set "advfile" to ""
    advfile = ""

    # Loop through adventure references
    for ref in refs:

        # If the references ID == the data's adventure id
        if ref["id"] == data["advid"]:

            # Set "advfile" to the path to the adventure data file.
            advfile = ref["file"]
    
    # Print "advfile" (debugging only)
    print(advfile)

    # Set "advfile" to the json contents of "advfile"
    advfile = json.load(open(advfile,"r"))link

    # Loop through events in "advfile"
    for event in advfile["events"]:

        # If the event's ID == the ID of the initial event
        if event["id"] == advfile["initEvt"]:

            # Print "Handling" (debugging only)
            print("Handling")

            # Handle the event
            handleEvent(event,advfile,data["id"])


# Handler For Joining Room
@sio.on("room")
def joinRoom(data):
    # Join client to room specified in data
    join_room(data)

sio.run(app,port=3436,host="0.0.0.0",debug=True)