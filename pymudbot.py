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
                tn_conn = self.telnet_handler(msg)
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
        # print(processed_frame)
        if out_buffer:
            print("Outbuffer received")
            print(out_buffer)
            print(out_buffer.decode(encoding="utf-8", errors="ignore"))
            print("Processed frame:")
            print(processed_frame)
            print("Unprocessed frame:")
            print(frame.data[0])
            print(out_events)

    async def handle_msg(self, msg):
        """
        This will handle incoming messages, negotiate telnet options, etc.
        """
        self.logTask = asyncio.create_task(self.log(msg))
        await self.logTask
        text = msg.decode(encoding="utf-8", errors="ignore")
        if "connect" in text.lower():
            print("Found Connect!")
            await self.writer.drain()
            self.writer.write_eof

    async def request(self, msg):
        self.writer.write(msg)
        return await self.reader.readline()


if __name__ == "__main__":

    # Get host & port
    # TODO: Uncomment before push
    hostname = pyip.inputURL("What host are we connecting to? ")
    pt = pyip.inputInt("What port? ")
    bot_user = pyip.inputStr("What's the bot name?")
    bot_pass = pyip.inputStr("What's the bot password?")

    # Instantiate session
    session = SessionHandler()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(session.connect(host=hostname, port=pt))
    loop.close()
