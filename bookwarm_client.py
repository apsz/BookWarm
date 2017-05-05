#!/usr/bin/python3


import asyncio


class BookWarmClient(asyncio.Protocol):
    message = 'Hello'

    def connection_made(self, transport):
        transport.write(self.message.encode())
        print('data sent: {}'.format(self.message))

    def data_received(self, data):
        print('data received: {}'.format(data.decode()))

    def connection_lost(self, exc):
        print('server closed the connection')
        asyncio.get_event_loop().stop()


def main():
    loop = asyncio.get_event_loop()
    coro = loop.create_connection(BookWarmClient, 'localhost', 23)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()


if __name__ == '__main__':
    main()