#! /usr/bin/python3
import threading
import time
import queue
import socketio
import collections
import json
import os
import sys
import asyncio
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

parties = []    
invites = []
clients = []
from multiprocessing import Process
app = Flask(__name__)
sio = SocketIO(app)


@sio.on('startingParty')
async def startingParty(sid,data):
    data=json.loads(data)
    parties.append({"PartyID":os.urandom(32),"OwnerSID":sid,"OwnerUNAME":data[0],"Members":[sid]})

@sio.on('invitingToParty')
async def inviteingToParty(sid,data):
    data=json.loads(data)
    for item in parties:
        if item["OwnerSID"] == sid:
           invites.append({"username":data[0],"partyid":item["PartyID"]})

@sio.on('checkIn')
async def checkIn(sid,data):
    data=json.loads(data)
    sio.save_session(sid,data)
    sio.emit("checkedIn",{"ok":True},room=sid)

@sio.on('checkOut')
async def checkOut(sid,data):
    data=json.loads(data)
    checkedIn = False
    i=0
    for item in clients:
        if item["ClientSID"] == sid:
            del clients[i]
            checkedIn=True
        i+=1
    sio.emit("checkedOut",{"checkedIn":checkedIn},roon=sid)
@sio.on('connect')
def connect(sio,environ):
    print(environ)

async def reportInvites():
    while True:
        i=0
        for item in invites:
            uname = item["username"]
            client = None
            for item in clients:
                if item["ClientUNAME"] == uname:
                    client = item
            if client != None:
                sio.emit("invitedToParty",room=client["ClientSID"])
success=True
print(len(sys.argv))
print(sys.argv)
if __name__ == "__main__" and len(sys.argv) == 1:
    app.run(port=3435)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(reportInvites())
elif len(sys.argv) > 1:
    if sys.argv[1] == "test":
        success=True
        print("Testing")
        server = Process(target=lambda: app.run(port=3435))
        server.start()
        time.sleep(10)
        if server.is_alive():
            server.terminate()
            server.join()
            exit(0)
        else:
            exit(1)