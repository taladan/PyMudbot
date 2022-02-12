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
    def __init__(self, bot, passwd):
        self.DEBUG = False
        self.bot = bot
        self.passwd = passwd
        self.connected = False
        self.encoding = "utf-8"
        self.commands = {
            "connect": (f"connect {self.bot} {self.passwd}\n"),
            "get_version": "@version",
        }

    async def connect(self, host: str, port: int):
        """
        handle connections
        """
        self.reader, self.writer = await asyncio.open_connection(host, port)
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
        # Simple log to file for now
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


def initialize_bot():
    """
    This checks for the existance of PyMudbot configuration database.
    If the database exists, load the database and return it.
    If the database doesn't exist, create the database, prompt for values
    write the info entered, then return that info.
    """
    print("Initializing PyMudBot")
    if DB_PATH.is_file():
        with shelve.open(DB_FILE) as db:
            hostname = db["hostname"]
            pt = db["mud_port"]
            bot_user = db["bot_user"]
            bot_pass = db["bot_pass"]
    else:
        # No DB. Get initial bot config info
        hostname = pyip.inputURL("What host are we connecting to?> ")
        pt = pyip.inputInt("What port?> ")
        bot_user = pyip.inputStr("What's the bot name?> ")
        bot_pass = pyip.inputStr("What's the bot password?> ")

        with shelve.open(DB_FILE) as db:
            db["hostname"] = hostname
            db["mud_port"] = pt
            db["bot_user"] = bot_user
            db["bot_pass"] = bot_pass
    return (hostname, pt, bot_user, bot_pass)


def run(hostname, pt, bot_user, bot_pass):
    # Instantiate session
    print("Setting up session")
    try:
        session = SessionHandler(bot_user, bot_pass)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(session.connect(host=hostname, port=pt))
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


if __name__ == "__main__":

    hostname, port, bot_name, password = initialize_bot()
    run(hostname, port, bot_name, password)
