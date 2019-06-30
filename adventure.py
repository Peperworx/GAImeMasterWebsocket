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



def handleEvent(event,adventure,id):
    if event["type"] == "say":
        sio.emit("gmSay",json.dumps(event),room=id)
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




@sio.on("room")
def joinRoom(data):
    join_room(data)

sio.run(app,port=3436,host="0.0.0.0",debug=True)