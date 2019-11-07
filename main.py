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



# Connect to redis
r = redis.Redis(host='127.0.0.1', port=6379, db=0)

# Custom handler for r.set
def rset(key,value):
    r.set(key, json.dumps(value))

# Custom handler for r.get
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


# Handling Checkin (Handshake)
@sio.on('checkIn')
def checkIn(data):

    # Print "(Clients sid) connected" (debug only)
    print("%s connected" % (request.sid))

    # Get "clients" from redis
    clients = rget("clients")

    # Append client to list of clients
    clients.append({"ClientSID":request.sid,"ClientUNAME":data})

    # Update "clients" on redis
    rset("clients", clients)

     
    #clientDict = rget("clientDict")
    #clientDict[request.sid] = len(clients)-1
    #rset("clientDict", clientDict)
    
    # Print list of clients (debug only)
    print(clients)

    # Delete list of clients
    del clients



# Handle client disconnecting
@sio.on('disconnect')
def disconnect():

    # Get list of clients from redis
    clients = rget("clients")

    # Get list of parties from redis
    parties = rget("parties")

    # Get list of games from redis
    games = rget("games")


    #clientDict = rget("clientDict")
    
    # Print "(Client sid) disconnected" (debug only)
    print("%s disconnected" % (request.sid))
    
    # Print lists of clients (debug only)
    print(clients)

    # Set "i" to zero
    i=0

    # Loop through list of parties
    for item in parties:

        # Set "i2" to zero
        i2=0

        # Loop through parties list of members
        for itm in item["Members"]:

            # If member ==  the clients sid
            if itm[1] == request.sid:

                # Remove member from party
                del parties[i]["Members"][i2]
                
                # Break
                break
            
            # Increment "i2"
            i2+=1
        
        # Increment "i"
        i+=1
    
    # Set "i" to zero
    i=0

    # Loop through games
    for item in games:

        # Set "i2" to zero
        i2=0

        # Loop through game's members
        for itm in item["Members"]:
            
            # If the members sid ==  the clients sid
            if itm[2] == request.sid:

                # Set id to members id
                id = games[i]["id"]

                # Remove member from game
                del games[i]["Members"][i2]

                # Emit "playerJoined" to refresh list of players
                sio.emit("playerJoined", games[i]["Members"], room=id)
            
            # Increment "i2"
            i2+=1
        
        # Increment "i"
        i+=1
    
    # Set i to zero
    i=0

    # Loop through list of clients
    for client in clients:

        # If the clients sid == the clients sid
        if client["ClientSID"] == request.sid:

            # Delete the client
            del clients[i]

            # Break
            break
        
        # Increment "i"
        i+=1
    #del clients[clientDict[request.sid]]

    # Update variables on redis
    rset("clients", clients)
    rset("parties", parties)
    rset("games", games)
    rset("clientDict", clientDict)

    # Cleanup variables (take out the trash)
    del clients
    del parties
    del games
    del clientDict


# Route / to a test page
@app.route("/")
def index():
    return open("test.html","r").read()


# Handle Starting Party
@sio.on('startingParty')
def startingParty(data):
    # Get parties from redis
    parties = rget("parties")

    # Parse JSON data
    data=json.loads(data)

    # Get SID
    sid = request.sid

    # Generate party ID
    iden = hashlib.sha224(os.urandom(16)).hexdigest()

    # Add party to parties
    parties.append({"PartyID":iden,"OwnerSID":sid,"OwnerUNAME":data[0],"Members":[[data[0],sid]]})
    
    # Update parties on redis
    rset("parties", parties)

    # Cleanup parties
    del parties

    # Send id to party
    sio.emit("hereIsID", {"id":iden})

    # Get chats from redis
    chats = rget("chats")

    # Create new subset in chats for party
    chats[iden] = []

    # Update chats on redis
    rset("chats",chats)

    # Cleannup chats
    del chats


# Handle inviting to party
@sio.on('invitingToParty')
def invitingToParty(data):
    
    # Get data from redis
    parties = rget("parties")
    data=json.loads(data)
    invites = rget("invites")

    # Get sid
    sid = request.sid

    # Loop through parties
    for item in parties:

        # If the owners SID == the clients sid
        if item["OwnerSID"] == sid:
            # Add client to list of invites
            invites.append({"username":data[0],"partyid":item["PartyID"],"OwnerUNAME":item["OwnerUNAME"]})
    
    # Update parties on redis
    rset("parties", parties)

    # Cleanup parties list
    del parties

    # Update invites on redis
    rset("invites",invites)

    # Cleanup invites list
    del invites

# Hander for joinPArty
@sio.on('joinParty')
def joinParty(data):
    
    # Parse data
    data = json.loads(str(data))

    # Get partyID
    partyID = data[0]

    # Get uname
    uname = data[1]

    # Get parties
    parties = rget("parties")

    # Set "i" to zero
    i=0

    # Loop through parties
    for item in parties:

        # If item's partyID  == partyID
        if item["PartyID"] == partyID:

            # If Owners SID does not equal clients sid
            if item["OwnerSID"] != request.sid:

                # Append member to party
                parties[i]["Members"].append([uname,request.sid])

                # Loop through Member in members
                for itm in item["Members"]:

                    # Tell the member that someone has joined party
                    sio.emit("memberJoiningParty",[uname,item],room=itm[1])
        
        # Increment "i"
        i+=1
    
    # Update parties on redis
    rset("parties", parties)

    # Cleanup parties
    del parties

# Handle leftParty
@sio.on("leftParty")
def leftParty(data):

    # Get parties from redis
    parties = rget("parties")

    # Set "i" to zero
    i=0

    # Loop through parties
    for item in parties:

        # Set "i2" to zero
        i2=0

        # Loop through memebrs
        for itm in item["Members"]:

            # If member id  == data
            if itm[0] == data:
                # Delete member from party
                del parties[i]["members"][i2]

                # Emit memberJoiningParty to party
                sio.emit("memberJoiningParty", [data,item], room=item["PartyID"])

            # Increment "i2"
            i2+=1
        
        # Increment "i"
        i+=1
    
    # Update parties on redis
    rset("parties", parties)

    # Cleanup parties
    del parties

# Handle sendChat
@sio.on("sendChat")
def sendChat(data):

    # Get chats from redis
    chats = rget("chats")

    # Emit newMsg to party
    sio.emit("newMsg", data, room=data["partyID"])
    
    # Append message to party's chat list
    chats[data["partyID"]].append(data)

    # Update chats on redis
    rset("chats", chats)

    # Cleanup chats
    del chats


# Handle joining room
@sio.on("room")
def joinRoom(data):

    # Connect client to room
    join_room(data)


# Handle selectCharacter
@sio.on("selectCharacter")
def selectCharacter(data):
    clients = rget("clients")
    i=0
    for item in clients:
        if item["ClientUNAME"] == data["UNAME"]:
            clients[i]["SelectedCharacter"] = data["CHARID"]
            break
        i+=1
    rset("clients",clients)


def getDefaultChar(uname):
    pass


@sio.on("startGame")
def startGame(data):
    print(data)
    games= rget("games")
    games.append({"id":data[0],"Members":[]})
    sio.emit("gameStarting","",room=data[0])
    rset("games",games)
    del games


@sio.on("joinGame")
def joinGame(data):
    games = rget("games")
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
    rset("games",games)
    del games


def reportInvites():
    while True:
        i=0
        invites = rget("invites")
        clients = rget("clients")
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
        rset("clients",clients)
        del clients
        rset("invites",invites)
        del invites


success=True
print(len(sys.argv))
print(sys.argv)


if __name__ == "__main__" and len(sys.argv) == 1:
    rset("invites",[])
    rset("clients", [])
    reportingThread = threading.Thread(target=reportInvites)
    reportingThread.start()
    sio.run(app,port=3435,host="0.0.0.0",debug=True, cors_allowed_origins="*")
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