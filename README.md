# GAImeMasterWebsocket
Websocket server for [gAImeMaster](https://github.com/wireboy5/GAImeMaster)

## What it does
gAImeMasterWebsocket is the websocket backend for [gAImeMaster](https://github.com/wireboy5/GAImeMaster)
It handles things such as creating and joining parties, handling chat messages, and handling adventures.

## Instructions for running:
### Linux:
Install python3 if you have not already:
```bash
sudo apt install python3 python3-pip
```
Clone from github:
```bash
git clone https://github.com/wireboy5/GAImeMasterWebsocket.git
```

CD into the folder you cloned gAImeMasterWebsocket to:
```bash
cd GAImeMasterWebsocket
```

Install requirements:
```bash
sudo pip3 install requirements.txt
```

Run main.py:
 ```bash
 nohup python3 main.py &
 ````
 
Run adventure.py:
 ```bash
  nohup python3 adventure.py.py &
 ````

And thats it! You are now running the gAImeMaster's websocket backend.
