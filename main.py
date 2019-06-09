#! /usr/bin/python3
import threading
import time
import queue
import collections
import json
import os
import hashlib
import sys
import asyncio
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room

parties = []    
invites = []
clients = []
games = []
clientDict = {}
from multiprocessing import Process
app = Flask(__name__)
sio = SocketIO(app,async_mode = 'threading')

@sio.on('checkIn')
def checkIn(data):
    print("%s connected" % (request.sid))
    clients.append({"ClientSID":request.sid,"ClientUNAME":data})
    clientDict[request.sid] = len(clients)-1
    print(clients)
    
@sio.on('disconnect')
def disconnect():
    print("%s disconnected" % (request.sid))
    print(clients)
    i=0
    for item in parties:
        i2=0
        for itm in item["Members"]:
            if itm[1] == request.sid:
                del parties[i]["Members"][i2]
                break
            i2+=1
        i+=1
    i=0
    for item in games:
        i2=0
        for itm in item["Members"]:
            
            if itm[2] == request.sid:
                id = games[i]["id"]
                del games[i]["Members"][i2]
                sio.emit("playerJoined", games[i]["Members"], room=id)
            i2+=1
        i+=1
    del clients[clientDict[request.sid]]

@app.route("/")
def index():
    return open("test.html","r").read()


@sio.on('startingParty')
def startingParty(data):
    data=json.loads(data)
    sid = request.sid
    id = hashlib.sha224(os.urandom(16)).hexdigest()
    parties.append({"PartyID":id,"OwnerSID":sid,"OwnerUNAME":data[0],"Members":[[data[0],sid]]})
    sio.emit("hereIsID", {"id":id})


@sio.on('invitingToParty')
def invitingToParty(data):
    data=json.loads(data)
    sid = request.sid
    for item in parties:
        if item["OwnerSID"] == sid:
           invites.append({"username":data[0],"partyid":item["PartyID"],"OwnerUNAME":item["OwnerUNAME"]})


@sio.on('joinParty')
def joinParty(data):
    partyID = data[0]
    uname = data[1]
    i=0
    for item in parties:
        if item["PartyID"] == partyID:
            if item["OwnerSID"] != request.sid:
                parties[i]["Members"].append([uname,request.sid])
                for itm in item["Members"]:
                    sio.emit("memberJoiningParty",[uname,item],room=itm[1])
        i+=1

@sio.on("leftParty")
def leftParty(data):
    i=0
    for item in parties:
        i2=0
        for itm in item["Members"]:
            if itm[0] == data:
                del parties[i]["members"][i2]
                sio.emit("memberJoiningParty", [data,item], room=item["PartyID"])
            i2+=1
        i+=1
@sio.on("sendChat")
def sendChat(data):
    sio.emit("newMsg", data, room=data["partyID"])


@sio.on("room")
def joinRoom(data):
    join_room(data)


@sio.on("selectCharacter")
def selectCharacter(data):
    i=0
    for item in clients:
        if item["ClientUNAME"] == data["UNAME"]:
            clients[i]["SelectedCharacter"] = data["CHARID"]
            break
        i+=1


def getDefaultChar(uname):
    pass


@sio.on("startGame")
def startGame(data):
    print(data)
    global games
    games.append({"id":data[0],"Members":[]})
    sio.emit("gameStarting","",room=data[0])


@sio.on("joinGame")
def joinGame(data):
    partyId = data["ID"]
    uname = data["UNAME"]
    charid = data["CHARID"]
    members = []
    for game in games:
        if game["id"] == partyId:
            game["Members"].append([uname,charid,request.sid])
            members = game["Members"]
            print(members)
    sio.emit("playerJoined", members, room=partyId)


def reportInvites():
    while True:
        i=0
        for itm in invites:
            uname = itm["username"]
            client = None
            for item in clients:
                if item["ClientUNAME"] == uname:
                    client = item
            if client != None:
                sio.emit("invitedToParty", {"PartyID":str(itm["partyid"]),"OwnerUNAME":json.dumps(itm["OwnerUNAME"]),"Party":json.dumps(itm)},room=client["ClientSID"])
                del invites[i]
                print("Invited "+uname+" or: "+client["ClientSID"])
            i+=1


success=True
print(len(sys.argv))
print(sys.argv)


if __name__ == "__main__" and len(sys.argv) == 1:
    reportingThread = threading.Thread(target=reportInvites)
    reportingThread.start()
    sio.run(app,port=3435,host="0.0.0.0",debug=True)
    reportingThread.join()
elif len(sys.argv) > 1:
    if sys.argv[1] == "test":
        success=True
        print("Testing")
        server = Process(target=lambda: sio.run(app,port=3435,debug=False))
        server.start()
        time.sleep(10)
        if server.is_alive():
            server.terminate()
            server.join()
            exit(0)
        else:
            exit(1)