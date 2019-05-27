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
from flask_socketio import SocketIO, emit

parties = []    
invites = []
clients = []
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
    del clients[clientDict[request.sid]]
    print(clients)

@app.route("/")
def index():
    return open("test.html","r").read()


@sio.on('startingParty')
def startingParty(data):
    data=json.loads(data)
    sid = request.sid
    parties.append({"PartyID":hashlib.sha224(os.urandom(16)).hexdigest(),"OwnerSID":sid,"OwnerUNAME":data[0],"Members":[[data[0],sid]]})

@sio.on('invitingToParty')
def invitingToParty(data):
    data=json.loads(data)
    sid = request.sid
    for item in parties:
        if item["OwnerSID"] == sid:
           invites.append({"username":data[0],"partyid":item["PartyID"],"OwnerUNAME":item["OwnerUNAME"]})

@sio.on('joinParty')
def joinParty(data):
    data = json.loads(data)
    partyId =  data[0]
    i=0
    party = ""
    for item in parties:
        if item["PartyID"] == partyId:
            parties[i]["Members"].append([data[1],data[0]])
            party = item
        i+=1
    if party != "":
        sio.emit("joiningParty", [False,data[1],sid], room=party["OwnerSID"])
        sio.emit("joiningParty", [True,partyID], room=sid)
    else:
        sio.emit("partyNotAvailible",[partyId],room=sid)
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