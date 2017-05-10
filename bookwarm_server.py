#!/usr/bin/python3


import os
import sys
import argparse
import asyncio

import bookwarm
from bookwarm_serverproto import ServerProtocol


class BookWarmServer:

    def __init__(self, server_name, host, port, loop):
        self._server_name = server_name
        self._host = host
        self._port = port
        self._loop = loop
        self._active_users = set()
        self._database_path = self._setup_database()
        self.__all_books = self._load_all_available_books()

    @property
    def all_books(self):
        return self.__all_books

    def run(self):
        serv_coro = self._loop.create_server(
            protocol_factory=lambda: ServerProtocol(self),
            host=self._host,
            port=self._port)
        return self._loop.run_until_complete(serv_coro)

    def add_user(self, new_user):
        if new_user in self._active_users:
            return False
        self._active_users.add(new_user)
        return True

    def remove_user(self, user):
        self._active_users.remove(user)

    def get_user_collections(self, user):
        with bookwarm.SQLSession(self._database_path) as session:
            return session.query(bookwarm.BookCollection).filter(
                bookwarm.BookCollection.user == user).all()

    def get_collection_by_name(self, collection_name):
        with bookwarm.SQLSession(self._database_path) as session:
            return session.query(bookwarm.BookCollection).filter(
                bookwarm.BookCollection.collection_name == collection_name).one()

    def find_book_by_isbn(self, isbn):
        with bookwarm.SQLSession(self._database_path) as session:
            return session.query(bookwarm.Book).filter(
                bookwarm.Book.isbn == isbn).all()

    def add_new_book(self, isbn):
        if not self.find_book_by_isbn(isbn):
            pass

    def add_new_collection(self, user, collection_name):
        new_collection = bookwarm.BookCollection(user=user,
                                                 collection_name=collection_name,
                                                 book_collection=[])

    def _setup_database(self):
        try:
            data_folder = os.path.join(os.path.dirname(__file__), 'data')
            if not os.path.exists(data_folder):
                os.mkdir(data_folder)
            database_file_path = os.path.join(data_folder, 'bookwarm.db')
            if not os.path.exists(database_file_path):
                bookwarm.setup_database(database_file_path)
            return database_file_path
        except (EnvironmentError, IOError) as data_setup_err:
            print('Server cannot create necessary database folder/file: {}\n'
                  'Exiting...'.format(data_setup_err))
            sys.exit()

    def _load_all_available_books(self):
        with bookwarm.SQLSession(self._database_path) as session:
            self.__all_books = session.query(bookwarm.UserBook).all()


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