#!/usr/bin/python3


import asyncio
import getpass

import CmdUtils


class BookWarmClient(asyncio.Protocol):

    def __init__(self, user):
        self._user = user
        self._menus = dict(main_menu=self._main_menu_options,
                           books_menu=self._books_menu_options,
                           empty_books_menu=self._books_empty_options,
                           collections_menu=self._collections_menu_options,
                           empty_collections_menu=self._collections_empty_options)

    @property
    def user(self):
        return self._user

    def connection_made(self, transport):
        self._transport = transport
        self._write(self._user)

    def data_received(self, raw_data):
        decoded_data = raw_data.decode('utf-8')

        status, command, reply = decoded_data.split('  ')
        self._handle_server_data(status, command, reply)

    def connection_lost(self, exc):
        print('Server closed the connection.')
        asyncio.get_event_loop().stop()

    def _handle_server_data(self, status, command, reply):
        if status not in {'OK', 'RE'}:
            print(reply)
            self.quit()

        if status == 'RE':
            print(reply)

        self._menus[command]()

    def _main_menu_options(self):
        user_choice = CmdUtils.get_str('(A)ll books  (M)y Collections  (Q)uit',
                                       input_type='option', valid='amq')
        self._send_formatted(command=user_choice, client_data='', options_menu='main_menu')

    def _books_empty_options(self):
        user_choice = CmdUtils.get_str('(A)dd Book  (B)ack', input_type='option', valid='ab')
        if user_choice == 'a':
            new_book_data = self._get_book_data()
            self._send_formatted(command=user_choice, client_data=new_book_data,
                                 options_menu='books_menu')
        else:
            self._main_menu_options()

    def _books_menu_options(self):
        user_choice = CmdUtils.get_str('(A)dd Book  (V)iew  (E)dit  (D)elete  (B)ack',
                                       input_type='option', valid='avedb')
        if user_choice == 'b':
            self._main_menu_options()
        else:
            self._send_formatted(command=user_choice, client_data='',
                                 options_menu='collections_menu')

    def _collections_empty_options(self):
        user_choice = CmdUtils.get_str('(C)reate  (B)ack', input_type='option', valid='cb')
        if user_choice == 'c':
            collection_name = CmdUtils.get_str('Collection name', input_type='string', min_len=1)
            self._send_formatted(command=user_choice, client_data=collection_name,
                                 options_menu='collections_menu')
        else:
            self._main_menu_options()

    def _collections_menu_options(self):
        user_choice = CmdUtils.get_str('(A)dd Collection  (V)iew  (E)dit  (D)elete  (B)ack',
                                       input_type='option', valid='vedb')
        self._send_formatted(command=user_choice, client_data='', options_menu='collections_menu')

    def _get_isbn(self):
        isbn = CmdUtils.get_int('ISBN (10 or 13 plaint digits)', input_type='isbn')
        if not (isinstance(isbn, int) and (len(str(isbn)) == 10 or len(str(isbn)) == 13)):
            raise ValueError('ISBN must be non-empty integer of 10 or 13 digits.')
        return isbn

    def _get_book_data(self):
        raise NotImplementedError()

    def quit(self, *ignore):
        asyncio.get_event_loop().stop()

    def _write(self, text):
        self._transport.write(text.encode('utf-8'))

    def _send_formatted(self, command, client_data, options_menu, format='{}  {}  {}'):
        self._write(format.format(command, client_data, options_menu))


def get_user():
    return getpass.getuser()


def main():
    user = get_user()
    loop = asyncio.get_event_loop()
    coro = loop.create_connection(lambda: BookWarmClient(user),
                                  'localhost', 23)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()


if __name__ == '__main__':
    main()