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
        self.__all_books = []
        self._load_all_available_books()

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
        self._active_users.discard(user)

    def get_user_collections(self, user):
        with bookwarm.SQLSession(self._database_path) as session:
            return session.query(bookwarm.BookCollection).filter(
                bookwarm.BookCollection.user == user).all()

    def get_collection_by_name(self, collection_name):
        with bookwarm.SQLSession(self._database_path) as session:
            return session.query(bookwarm.BookCollection).filter(
                bookwarm.BookCollection.collection_name == collection_name).all()

    def add_new_collection(self, user, collection_name):
        with bookwarm.SQLSession(self._database_path) as session:
            try:
                new_collection = bookwarm.BookCollection(user, collection_name, [])
                session.add(new_collection)
                session.commit()
                return (True, '')
            except Exception as add_collection_err:
                session.rollback()
                return (False, add_collection_err)

    def delete_collection(self, collection_name):
        with bookwarm.SQLSession(self._database_path) as session:
            try:
                collections = session.query(bookwarm.BookCollection).all()
                for collection in collections:
                    if collection.collection_name == collection_name:
                        session.delete(collection)
                        session.commit()
                return (True, '')
            except Exception as del_collection_err:
                session.rollback()
                return (False, del_collection_err)

    def find_book_by_isbn(self, isbn):
        with bookwarm.SQLSession(self._database_path) as session:
            books = session.query(bookwarm.Book).all()
            for book in books:
                if book.isbn == int(isbn):
                    return book
        return False

    def retrieve_book_details(self, isbn):
        book_attrs = ('title', 'author', 'genre', 'no_of_pages',
                      'year_published', 'edition', 'publisher')

        with bookwarm.SQLSession(self._database_path) as session:
            books = session.query(bookwarm.Book).all()
            for book in books:
                if book.isbn == int(isbn):
                    book_data = '\n'.join([str(book.__getattribute__(attr)) for attr in book_attrs])
                    return book_data
        return False

    def add_new_book(self, book_data):
        with bookwarm.SQLSession(self._database_path) as session:
            try:

                prepared_data = [int(value) if value.isdigit()
                                            else value for value in book_data.split()]
                new_book = bookwarm.Book(*prepared_data)
                session.add(new_book)
                session.commit()
                self._load_all_available_books()
                return (True, '')
            except Exception as add_book_err:
                session.rollback()
                return (False, add_book_err)

    def delete_book(self, isbn):
        with bookwarm.SQLSession(self._database_path) as session:
            try:
                books = session.query(bookwarm.Book).all()
                for book in books:
                    if book.isbn == int(isbn):
                        session.delete(book)
                        session.commit()
                self._load_all_available_books()
                return (True, '')
            except Exception as del_book_err:
                session.rollback()
                return (False, del_book_err)

    def update_book(self, isbn, edition, publisher):
        with bookwarm.SQLSession(self._database_path) as session:
            try:
                books = session.query(bookwarm.Book).all()
                for book in books:
                    if book.isbn == int(isbn):
                        if not edition == 'None':
                            book.edition = int(edition)
                        if not publisher == 'None':
                            book.publisher = publisher
                        session.commit()
                self._load_all_available_books()
                return (True, '')
            except Exception as book_upd_err:
                session.rollback()
                return (False, book_upd_err)

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
            self.__all_books = session.query(bookwarm.Book).all()


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