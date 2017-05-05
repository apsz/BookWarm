#!/usr/bin/python3


import sys
import argparse
import asyncio
from bookwarm_serverproto import ServerProtocol


class BookWarmServer:

    def __init__(self, server_name, host, port, loop):
        self._server_name = server_name
        self._host = host
        self._port = port
        self._loop = loop
        self._user_collections = []
        self._all_books = {}

    def run(self):
        serv_coro = self._loop.create_server(
            protocol_factory=lambda: ServerProtocol(self),
            host=self._host,
            port=self._port)
        return self._loop.run_until_complete(serv_coro)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', type=str, default='BookWarm v. 0.1',
                        help='Server name')
    parser.add_argument('-H', '--host', type=str, default='',
                        help='Host to run on.')
    parser.add_argument('-p', '--port', type=int, default=23,
                        help='Port to run on.')
    args = parser.parse_args()
    return args.name, args.host, args.port


def main():
    server_name, host, port = get_args()

    loop = asyncio.get_event_loop()
    bookwarm_server = BookWarmServer(server_name, host, port, loop)
    bookwarm_server.run()
    loop.run_forever()


if __name__ == '__main__':
    main()