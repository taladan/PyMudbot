# PyMudbot.py

## What is PyMudbot?

PyMudbot aims to be a framework for connecting bots to muds.  Simply put:  There aren't enough annoying chatbots in the world, so we needed another framework!  

All joking aside, ever since there have been muds/mushes/mux's/moo's/circles/smaugs/dikus/lps, etc, there has been a desire for the ability to have automata that could connect and interact with the environment and players.  This framework will (eventually) allow you to run multiple bot instances (to multiple muds if you like!) and have each of them respond according to their own configurations.  

As it stands, you are currently (mostly) able to add as many bots as you like and they can connect to their proper hostnames -- as long as the information you input is correct - I still have to work on error handling connections with malformed connection data.  They don't do anything else yet as of this writing (and if you notice they do, ping me to update the README).  

Below you'll find the current roadmap of functionality.  If it's checked off, it's in place and mostly working.  If it's not checked off, it's in the 'TODO' pile.  You probably could've figured that out, but I like overexplaining things so we're all on the same page.

If you find any bugs, submit an issue.  If you have any suggestions, post them over in discussions!

If you like what you see and you'd like to contribute, go ahead and fork the project and make a pull request.


## Resources to review and understand
Current code: [PyMudbot Repo](https://github.com/taladan/mudbot/blob/master/pymudbot.py)
Cribbed from: [Stackoverflow](https://stackoverflow.com/questions/38562891/how-to-create-telnet-client-with-asyncio)

### Protocol reading list
[A short explanation of what Telnet is](https://www.extrahop.com/resources/protocols/telnet/)
[telnet lib](https://docs.python.org/3/library/telnetlib.html)
[Mudtelnet lib](https://github.com/volundmush/mudtelnet-python)
[Telnet Negotiation](http://mud-dev.wikidot.com/telnet:negotiation)
[MXP](https://www.zuggsoft.com/zmud/mxp.htm)
[MTTS](https://tintin.mudhalla.net/protocols/mnes/)
[MSP](https://www.zuggsoft.com/zmud/msp.htm)

## Libraries used:
- [asyncio](https://docs.python.org/3/library/asyncio.html)
- [Mudtelnet](https://github.com/volundmush/mudtelnet-python)
- [PyInputPlus](https://pyinputplus.readthedocs.io/en/latest/)
- [shelve](https://docs.python.org/3/library/shelve.html)

### Possible Libs to include:
- [Python-statemachine](https://pypi.org/project/python-statemachine/)


## Roadmap

### Configuration
- [x] If bots haven't been set up, run initial setup
	- [x] Get hostname
	- [x] get port
	- [x] get bot name
	- [x] get bot password
	- [x] write to db (shelf file)
- [x] if bots exist in db, load bot configs
- [ ] connect to bot(s)
	- [ ] Connect to all bots
	- [ ] Choose which bots to connect
- [x] Start menu:
	- [x] Add Bot
	- [x] Edit Bot
	- [x] Delete Bot
	- [x] QUIT

### Connection
- [x] Prompt for server to connect to
- [x] Prompt for port for connection
- [x] Prompt for bot name
- [x] Prompt for bot password
- [x] Establish socket with server
- [x] If server doesn't exist/timesout notify & exit
- [x] Where in the stream does the telnet server send the negotiation options (IAC/DO/WILL/WONT, etc)? 
- [x] How do I see those options and respond?
- [x] Connect to a playable DBREF
- [ ] Determine mud type (Penn, Tiny, Mux, Lp, Circle, Diku, Smaug, ROM, j Custom)

### Mud interaction
- [ ] Ability to join channels
- [ ] Listen for player commands
- [ ] Respond to player commands
- [ ] Error handling on connect
- [ ] How to handle lines

### Player interaction
- [ ] How to search for triggers
- [ ] How to process triggers
- [ ] How to respond to triggers
- [ ] How to determine state
- [ ] How to process state
- [ ] How to respond to state
- [ ] Remember players (?)
- [ ] Remember player commands (?)
 