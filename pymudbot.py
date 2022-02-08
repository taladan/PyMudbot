#! bin/python

import asyncio


class SessionHandler:
    async def connect(self, host: str, port: int):
        self.reader, self.writer = await asyncio.open_connection(host, port)

        while True:
            msg = await self.reader.readline()
            if msg is None:
                asyncio.sleep(1)
                continue
            self.handle_msg(msg)

    def handle_msg(self, msg):
        print(msg)

    async def request(self, msg):
        self.writer.write(msg)
        return await self.reader.readline()


if __name__ == "__main__":
    session = SessionHandler()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(session.connect(host="winter.mushpark.com", port=3000))
    loop.close()
