#! bin/python

import asyncio
import mudtelnet as mt
import os
import pyinputplus as pyip
import shelve
import sys
from pathlib import Path

# CONSTANTS

DB_FILE = "bot_config.db"
MUDBOT_ROOT = Path.cwd()
DB_PATH = Path(MUDBOT_ROOT / DB_FILE)


class SessionHandler:
    def __init__(self, host, port, bot, passwd):

        self.DEBUG = False
        self.host = host
        self.port = port
        self.bot = bot
        self.passwd = passwd
        self.connected = False
        self.encoding = "utf-8"
        self.commands = {
            "connect": (f"connect {self.bot} {self.passwd}\n"),
            "get_version": "@version",
        }

    async def connect(self):
        """
        handle connections
        """
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        connect_cmd = bytes(f"connect {self.bot} {self.passwd}\n", "utf-8")

        while True:
            bytes_line = await self.reader.readline()
            if bytes_line is None:
                await asyncio.sleep(0.25)
                continue
            else:
                tn_conn = await self.telnet_handler(bytes_line)
                if tn_conn and not self.connected:
                    # Not connected?  Connect.
                    self.writer.write(
                        bytes(f"{self.commands['connect']}", self.encoding)
                    )
                    await asyncio.sleep(0.25)
                    continue
                if tn_conn and self.connected:
                    # What to do once we're connected
                    self.writer.write(
                        bytes(f"{self.commands['get_version']}", self.encoding)
                    )

    async def log(self, bytes_line):
        """
        Simple log to file for now
        this will most likely be replaced with logger in the near future
        """
        with open("mudbot.log", "ab") as logfile:
            logfile.write(bytes_line)
        if self.DEBUG:
            print(f"Writing output to {os.curdir}{logfile.name}")

    async def telnet_handler(self, bytes_line):
        """
        Handle telnet negotiation
        The telnet connection needs to be persistent through the session and handle all lines recieved.
        """
        if self.DEBUG:
            self.logTask = asyncio.create_task(self.log(bytes_line))
            await self.logTask

        tn_conn = mt.TelnetConnection()
        out_buffer = bytearray()
        out_events = list()
        frame, size = mt.TelnetFrame.parse(bytes_line)
        processed_frame = tn_conn.process_frame(frame, out_buffer, out_events)
        if out_buffer:
            self.writer.write(out_buffer)
            await self.writer.drain()
            return True

    async def request(self, bytes_line):
        self.writer.write(bytes_line)
        return await self.reader.readline()


def make_new_bot():
    """
    Create new bot in the database
    The Data structure is as follows:
        db.bots = {"Bot1":{"name":"Botname", "host":"host.web.address", "port": PORTINT, "passwd":"bot_passwd"},
            "Bot2":{"name":"Botname2", "host":"host.web.address", "port": PORTINT, "passwd":"bot_passwd"},
            etc...
        }
    """
    hostname = pyip.inputURL("What host are we connecting to?> ")
    pt = pyip.inputInt("What port?> ")
    bot_name = pyip.inputStr("What's the bot name?> ")
    pw = pyip.inputStr("What's the bot password?> ")
    bot_file = {
        bot_name: {"name": bot_name, "host": hostname, "port": pt, "passwd": pw}
    }

    # Write to shelf
    db = shelve.open(DB_FILE)
    db.update(bot_file)
    db.close()
    return (hostname, pt, bot_name, pw)


async def intialize():
    """
    Checks for the existance of PyMudbot configuration database.
    If the database exists, load the database and return it.
    If not, make a new bot
    """
    print("Running PyMudBot initialization sequence...")
    if DB_PATH.is_file():
        print("PyMudbot database found!  Loading bots...")
        bots = shelve.open(DB_FILE)
        for bot in bots:
            print(f"Loading {bot}...")
            hostname = bots[bot]["host"]
            pt = bots[bot]["port"]
            bot_name = bots[bot]["name"]
            passwd = bots[bot]["passwd"]
            await run(hostname, pt, bot_name, passwd)
        bots.close()
    else:
        # No DB. Get initial bot config info
        hostname, port, bot, passwd = make_new_bot()
        await run(hostname, port, bot, passwd)


async def run(hostname, pt, bot_user, bot_pass):
    """
    Create session for indivitual bot
    """
    try:
        session = SessionHandler(hostname, pt, bot_user, bot_pass)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(await session.connect())
        loop.close()
    except KeyboardInterrupt as e:
        print(f"Caught signal {e}. Exiting")
    except SystemExit as e:
        print(f"Caught Signal {e}.  Exiting.")
        raise e
    except BaseException as e:
        print(e)
        print("Fatal Error. Exiting.")
        raise e
    finally:
        sys.exit()


def bot_query():
    """
    Query user for new bot creation
    """
    response = pyip.inputYesNo("Should I make a new bot? ", default="No", timeout=5.0)
    return True if response == "yes" else False


if __name__ == "__main__":

    response = bot_query()
    while response:
        hostname, port, bot_name, _ = make_new_bot()
        print(f"Created new bot ({bot_name}) for {hostname} at port #{port}.")
        response = bot_query()
    asyncio.run(intialize())
