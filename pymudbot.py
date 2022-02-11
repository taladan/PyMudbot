#! bin/python

import asyncio
import pyinputplus as pyip
import os
import sys
import mudtelnet as mt


class SessionHandler:
    def __init__(self):
        self.DEBUG = False

    async def connect(self, host: str, port: int):
        """
        handle connections
        """
        self.reader, self.writer = await asyncio.open_connection(host, port)

        while True:
            msg = await self.reader.readline()
            if msg is None:
                asyncio.sleep(0.25)
                continue
            else:
                response = await self.handle_msg(msg)

    async def log(self, msg):
        # Simple log to file for now
        with open("mudbot.log", "ab") as logfile:
            logfile.write(msg)
        if self.DEBUG:
            print(f"Writing output to {os.curdir}{logfile.name}")

    def telnet_handler(self, msg):
        # This doesn't work
        tn_conn = mt.TelnetConnection()
        out_buffer = bytearray()
        out_events = list()
        frame, size = mt.TelnetFrame.parse(msg)
        processed_frame = tn_conn.process_frame(frame, out_buffer, out_events)
        if processed_frame[0]:
            print("foo")

    async def handle_msg(self, msg):
        """
        This will handle incoming messages, negotiate telnet options, etc.
        """
        reply = self.telnet_handler(msg)
        self.logTask = asyncio.create_task(self.log(msg))
        await self.logTask
        response = None
        return response or reply

    async def request(self, msg):
        self.writer.write(msg)
        return await self.reader.readline()


if __name__ == "__main__":

    # Get host & port
    hostname = pyip.inputURL("What host are we connecting to? ")
    pt = pyip.inputInt("What port? ")

    # Instantiate session
    session = SessionHandler()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(session.connect(host=hostname, port=pt))
    loop.close()
