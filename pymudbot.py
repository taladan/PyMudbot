#! bin/python

import asyncio
import mudtelnet as mt
import os
import pyinputplus as pyip
import shelve
import sys
from pathlib import Path
from getpass import getpass

# CONSTANTS

DB_FILE = "bot_config.db"
MUDBOT_ROOT = Path.cwd()
DB_PATH = Path(MUDBOT_ROOT / DB_FILE)
PROG_NAME = "PyMudbot"
VERSION = 0.1
AUTHOR = "D. J. Crosby"
WEBSITE = "https://github.com/taladan/PyMudbot"


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
        """
        Currently unused
        """
        self.writer.write(bytes_line)
        return await self.reader.readline()


async def intialize():
    """
    Checks for the existance of PyMudbot configuration database.
    If the database exists, load the database and return it.
    If not, make a new bot
    """
    print("Running PyMudBot initialization sequence...")
    if DB_PATH.is_file():
        print("PyMudbot database found!  Loading bots...")
        bot_db = shelve.open(DB_FILE)
        bot_tasks = []
        for bot in bot_db:
            print(f"Loading {bot}...")
            hostname = bot_db[bot]["host"]
            port = bot_db[bot]["port"]
            bot_name = bot_db[bot]["name"]
            passwd = bot_db[bot]["passwd"]
            bot_tasks.append(asyncio.create_task(run(hostname, port, bot_name, passwd)))
        await asyncio.gather(*bot_tasks)
        bot_db.close()
    else:
        # No DB. Get initial bot config info
        print("No config found, creating new bot.")
        while True:
            bot_info = add_bot()
            if bot_info != None:
                hostname, port, bot, passwd = bot_info
                break

        await run(hostname, port, bot, passwd)


async def run(hostname, port, bot_user, bot_pass):
    """
    Create session for indivitual bot
    """
    try:
        session = SessionHandler(hostname, port, bot_user, bot_pass)
        loop = asyncio.get_event_loop()
        await session.connect()
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


def user_query(question):
    """
    Query user for new bot creation
    """
    df = "No"
    response = pyip.inputYesNo(question + f" [Default: {df}]", default=df, blank=True)
    return True if response == "yes" else False


def start_menu():
    """
    Display a menu of options when starting from `if __name__ == '__main__':`
    This menu allows for dealing with bots pre-connection.  Current options are:
        - Add Bot -> Allows for adding of bot to config db
        - Delete Bot -> Allows for deletion of existing bot from config db
        - Edit Bot -> Allows for editing of bot attributes in config db
        - Connect Existing Bots -> Connects all bots
        - QUIT -> Exits PyMudbot
    """
    header_line = "*" * 45
    menu_header = f"{PROG_NAME} v.{VERSION} Bot Config Menu"
    options = ["Add Bot", "Delete Bot", "Edit Bot", "Connect existing Bots", "QUIT"]
    start = True
    while start:
        print()
        print(header_line)
        print(menu_header.center(len(header_line)))
        print(header_line)
        print("\n")
        response = pyip.inputMenu(options, numbered=True)
        if response == "Add Bot":
            print("Adding bot to config:")
            bot_info = add_bot()
            if bot_info != None:
                hostname, port, bot_name, _ = add_bot()
            continue
        elif response == "Delete Bot":
            print("Delete Bot:")
            print(delete_bot(choose_bot()))
            continue
        elif response == "Edit Bot":
            print("Edit Bot:")
            edit_bot(choose_bot())
            continue
        elif response == "Connect existing Bots":
            print("Connecting existing bots:")
            start = False
        elif response == "QUIT":
            print("Quitting...")
            sys.exit()


def edit_bot(bot: str) -> None:
    """
    Edit database entry of {bot}
    """
    if bot == None:
        return bot
    else:
        bots = shelve.open(
            DB_FILE, writeback=True
        )  # Need writeback because we're changing values
        atts = list(bots[bot].keys())
        atts.append("BACK")  # Opt for exit without editting
        bot_obj = bots[bot]
        choice = pyip.inputMenu(atts, numbered=True)
        if choice == "BACK":
            bots.close()
            return None
        else:
            original = current = bot_obj[choice]
            prompt = f"What would you like to change {choice} to? "

            print(f"Original value of {choice}: {original}")
            if isinstance(current, int):
                new = pyip.inputInt(prompt + "[INT] > ")
                bot_obj.update({choice: new})
            elif isinstance(current, bool):
                new = pyip.inputBool(prompt + "[BOOLEAN] > ")
                bot_obj.update({choice: new})
            elif isinstance(current, str):
                new = pyip.inputStr(prompt + "[STRING] > ")
                bot_obj.update({choice: new})

            print(f"Value of {choice} changed from {original} to {current} on {bot}.")

        bots.close()
        return None


def choose_bot():
    """
    Allows menu-ized choice of bots that exist in database
    """
    print("Choosing Bot:")
    bots = shelve.open(DB_FILE)
    botnames = list(bots.keys())
    choices = botnames.copy()
    choices.append("BACK")
    choice = pyip.inputMenu(choices, numbered=True)
    if choice not in botnames:
        bots.close()
        return None
    else:
        bots.close()
        return choice


def delete_bot(bot):
    """
    Removes a bot from the database.
    Warning!  This cannot be undone!
    """
    bot_database = shelve.open(DB_FILE)
    if bot == None:
        return bot
    elif bot in bot_database:
        prompt = (
            f"Are you sure you want to delete {bot}? <WARNING: This cannot be undone!> "
        )
        response = user_query(prompt)
        if response:
            # Delete bot from database
            del bot_database[bot]
            ret = f"Deleted {bot}"
    else:
        ret = f"{bot} not found in database."
    return ret


def add_bot():
    """
    Create new bot in the database
    The Data structure is as follows:
        db.bots = {"Bot1":{"name":"Botname", "host":"host.web.address", "port": PORTINT, "passwd":"bot_passwd"},
            "Bot2":{"name":"Botname2", "host":"host.web.address", "port": PORTINT, "passwd":"bot_passwd"},
            etc...
        }
    """
    hostname = pyip.inputURL("Enter hostname:> ")
    pt = pyip.inputInt("Enter port number:> ")
    bot_name = pyip.inputStr("Enter bot name:> ")
    pw = getpass("Enter bot password:> ")
    bot_file = {
        bot_name: {"name": bot_name, "host": hostname, "port": pt, "passwd": pw}
    }
    prompt = f"""
    Adding {bot_name} to the bot config database with password: {pw}
    To connect to the server {hostname} at port {pt}.
    
    Is this correct?"""
    confirm = user_query(prompt)
    if confirm:
        # Write to shelf
        bot_db = shelve.open(DB_FILE)
        bot_db.update(bot_file)
        bot_db.close()
        return (hostname, pt, bot_name, pw)
    else:
        print("Input Cancelled: Bot not created.")
        return None


if __name__ == "__main__":

    start_menu()
    asyncio.run(intialize())
