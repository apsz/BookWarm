#!/usr/bin/python3


import asyncio
import getpass
import datetime
import collections

import CmdUtils


class MenuCancel(Exception): pass


class BookWarmClient(asyncio.Protocol):


    BookNamed = collections.namedtuple('BookNamed', 'title author genre no_of_pages '
                                                    'year_published edition publisher')


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
        elif user_choice == 'e':
            self._find_isbn(fallback_menu='books_menu', callback_func='_edit_book')
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

    def _find_isbn(self, fallback_menu='empty_books_menu', callback_func='_add_new_book'):
        try:
            isbn = self._get_isbn()
        except ValueError as isbn_err:
            print(isbn_err)
            if fallback_menu == 'empty_books_menu':
                self._books_empty_options()
            else:
                self._books_menu_options()
        else:
            isbn_menu = '{} {}'.format(isbn, callback_func)
            self._send_formatted(command='f', client_data=isbn_menu,
                                 options_menu='books_menu')

    def _gather_book_data(self):
        try:
            title = self.__get_str_or_cancel(msg='Title (or "c" to cancel)', input_type='string',
                                             default='c', min_len=2)
            author = self.__get_str_or_cancel(msg='Author (or "c" to cancel)', input_type='string',
                                              default='c', min_len=2)
            genre = self.__get_str_or_cancel(msg='Genre (or "c" to cancel)', input_type='string',
                                             default='c', min_len=1)
            no_of_pages = self.__get_int_or_cancel(msg='Number of pages (or "c" to cancel)',
                                                   input_type='integer', default='c',
                                                   min_val=1, max_val=10000)
            year_published = self.__get_int_or_cancel(msg='Year published (or "c" to cancel)',
                                                      input_type='integer', default='c',
                                                      max_val=datetime.date.today().year)
            edition = self.__get_int_or_cancel(msg='Edition (or "c" to cancel)', input_type='integer',
                                               default='c', min_val=1)
            publisher = self.__get_str_or_cancel(msg='(Optional) Publisher (or "c" to cancel)',
                                                 input_type='string', default='', min_len=0)
        except MenuCancel:
            return False
        else:
            return ('{title} {author} {genre} {no_of_pages} {year_published} '
                    '{edition} {publisher}'.format(**locals()))

    def _add_new_book(self, new_isbn):
        if not new_isbn:
            print('Cannot continue: ISBN already in DB.')
            self._main_menu_options()
        else:
            new_book_data = self._gather_book_data()
            if not new_book_data:
                print('Canceled. Reverting to menu.')
                self._main_menu_options()
            else:
                new_book_data = '{} {}'.format(new_isbn, new_book_data)
                self._send_formatted(command='a', client_data=new_book_data,
                                     options_menu='books_menu')

    def _edit_book(self, isbn_or_data):
        isbn, book_data = self.__parse_isbn_book_data(isbn_or_data)
        if not isbn:
            print('Cannot find the matching ISBN.')
            self._books_menu_options()
        else:
            if not book_data:
                data_to_send = '{} {}'.format(isbn, '_edit_book')
                self._send_formatted(command='r', client_data=data_to_send,
                                     options_menu='books_menu')
            else:
                separated_book_data = book_data.split('\n')
                new_edition = None
                new_publisher = None
                original_data = BookWarmClient.BookNamed(*separated_book_data)
                menu = 'Editable: (E)dition  (P)ublisher ("c" to cancel)'

                try:
                    print('Title: {0.title}\nAuthor: {0.author}\nGenre: {0.genre}\n'
                          'Pages: {0.no_of_pages}\nYear published: {0.year_published}\n'
                          'Edition: {0.edition}\nPublisher: {0.publisher}'.format(original_data))
                    user_choice = self.__get_str_or_cancel(msg=menu, input_type='string',
                                                           default='c', valid='ep', min_len=1)
                    if user_choice == 'c':
                        raise MenuCancel()
                    elif user_choice == 'e':
                        new_edition = self.__get_int_or_cancel(msg='Edition (or "c" to cancel)',
                                                               input_type='integer', min_val=1,
                                                               default=original_data.edition)
                    elif user_choice == 'p':
                        new_publisher = self.__get_str_or_cancel(msg='Publisher (or "c" to cancel)',
                                                                 input_type='string', min_len=0,
                                                                 default=original_data.publisher)
                except MenuCancel:
                    self._books_menu_options()
                else:
                    if (original_data.edition, original_data.publisher) == (new_edition, new_publisher):
                        print('No changes found.')
                        self._books_menu_options()
                        return False
                    isbn_data = '{} {} {}'.format(isbn, new_edition, new_publisher)
                    self._send_formatted(command='e', client_data=isbn_data,
                                         options_menu='books_menu')
                    return True

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

    def __parse_isbn_book_data(self, isbn_or_data):
        isbn_data, book_data = (isbn_or_data.split(':'), None)
        isbn = isbn_data[0]
        if len(isbn_data) == 2:
            isbn, book_data = isbn_data
        return isbn, book_data

    def __get_str_or_cancel(self, **kwargs):
        user_str = CmdUtils.get_str(**kwargs)
        if user_str == 'c':
            raise MenuCancel()
        return user_str

    def __get_int_or_cancel(self, **kwargs):
        user_int = CmdUtils.get_int(**kwargs)
        if user_int == 'c':
            raise MenuCancel()
        return user_int

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