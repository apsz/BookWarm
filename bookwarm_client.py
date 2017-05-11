#!/usr/bin/python3


import asyncio
import getpass
import datetime

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
        if status == 'FUNC':
            self.__getattribute__(command)(reply)
        else:
            if status == 'RE':
                print(reply)

            self._menus[command]()

    def _main_menu_options(self):
        user_choice = CmdUtils.get_str('(A)ll books  (M)y Collections  (Q)uit',
                                       input_type='option', valid='amq')
        self._send_formatted(command=user_choice, client_data='None', options_menu='main_menu')

    def _books_empty_options(self):
        user_choice = CmdUtils.get_str('(A)dd Book  (B)ack', input_type='option', valid='ab')
        if user_choice == 'a':
            self._find_isbn(fallback_menu='empty_books_menu')
        else:
            self._main_menu_options()

    def _books_menu_options(self):
        user_choice = CmdUtils.get_str('(A)dd Book  (V)iew  (E)dit  (D)elete  (B)ack',
                                       input_type='option', valid='avedb')
        if user_choice == 'b':
            self._main_menu_options()
        elif user_choice == 'a':
            self._find_isbn(fallback_menu='books_menu')
        elif user_choice == 'd':
            self._delete_book()
        elif user_choice == 'v':
            self._view_book()
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
        try:
            isbn = CmdUtils.get_str('ISBN (10 or 13 plain digits)', input_type='isbn', min_len=10, max_len=13)
            if (len(isbn) == 10 or len(isbn) == 13) and isbn.isdigit():
                return isbn
            raise ValueError()
        except (ValueError, TypeError):
            raise ValueError('ISBN must be non-empty integer of 10 or 13 digits.')

    def _find_isbn(self, fallback_menu='empty_books_menu'):
        try:
            new_isbn = self._get_isbn()
        except ValueError as isbn_err:
            print(isbn_err)
            if fallback_menu == 'empty_books_menu':
                self._books_empty_options()
            else:
                self._books_menu_options()
        else:
            isbn_menu = '{} {}'.format(new_isbn, '_add_new_book')
            self._send_formatted(command='f', client_data=isbn_menu,
                                 options_menu='books_menu')

    def _gather_book_data(self):
        title = CmdUtils.get_str('Title (or "c" to cancel)', input_type='string',
                                 default='c', min_len=2)
        if title == 'c':
            return
        author = CmdUtils.get_str('Author (or "c" to cancel)', input_type='string',
                                  default='c', min_len=2)
        if author == 'c':
            return
        genre = CmdUtils.get_str('Genre (or "c" to cancel)', input_type='string',
                                 default='c', min_len=1)
        if genre == 'c':
            return
        no_of_pages = CmdUtils.get_int('Number of pages (or "c" to cancel)', input_type='integer',
                                       default='c', min_val=1, max_val=10000)
        if no_of_pages == 'c':
            return
        edition = CmdUtils.get_int('Edition (or "c" to cancel)', input_type='integer',
                                   default='c', min_val=1)
        if edition == 'c':
            return
        year_published = CmdUtils.get_int('Year published (or "c" to cancel)',
                                          input_type='integer', default='c',
                                          max_val=datetime.date.today().year)
        if year_published == 'c':
            return
        publisher = CmdUtils.get_str('(Optional) Publisher (or "c" to cancel)',
                                     input_type='string', default='', min_len=0)
        if publisher == 'c':
            return
        return ('{title} {author} {genre} {no_of_pages} {edition} '
                '{year_published} {publisher}'.format(**locals()))

    def _add_new_book(self, status_isbn):
        status, isbn = status_isbn.split()
        if status == 'DUPLICATE':
            print('Cannot continue: ISBN already in DB.')
            self._main_menu_options()
        else:
            new_book_data = self._gather_book_data()
            if not new_book_data:
                print('Canceled. Reverting to menu.')
                self._main_menu_options()
            else:
                new_book_data = '{} {}'.format(isbn, new_book_data)
                self._send_formatted(command='a', client_data=new_book_data,
                                     options_menu='books_menu')

    def _delete_book(self):
        try:
            isbn_to_delete = self._get_isbn()
        except ValueError as isbn_err:
            print(isbn_err)
            self._main_menu_options()
        else:
            self._send_formatted(command='d', client_data=isbn_to_delete,
                                 options_menu='books_menu')

    def _view_book(self):
        try:
            isbn_to_find = self._get_isbn()
        except ValueError as isbn_err:
            print(isbn_err)
            self._main_menu_options()
        else:
            self._send_formatted(command='v', client_data=isbn_to_find,
                                 options_menu='books_menu')

    def quit(self, msg=None):
        print(msg)
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