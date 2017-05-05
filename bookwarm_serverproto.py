#!/usr/bin/python3


import asyncio


class ServerProtocol(asyncio.Protocol):

    def __init__(self, bookwarm_server):
        self._bookwarm_server = bookwarm_server
        self._transport = None

    def connection_made(self, transport):
        self._transport = transport
        self._write('Server: hello')

    def data_received(self, raw_data):
        try:
            decoded_data = raw_data.decode('utf-8')
            self._write('Server: {}'.format(decoded_data))
        except UnicodeDecodeError as decode_err:
            self._transport.write(str(decode_err).encode('utf-8'))

    def connection_lost(self, exc):
        self._write('exiting')

    def _write(self, text):
        self._transport.write(text.encode('utf-8'))