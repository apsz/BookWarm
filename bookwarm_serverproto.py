#!/usr/bin/python3


import os
import asyncio


class ServerProtocol(asyncio.Protocol):

    def __init__(self, bookwarm_server):
        self._bookwarm_server = bookwarm_server
        self._transport = None
        self._user = None
        self._user_collections = []
        self._commands = dict(main_menu = dict(a=self._show_books,
                                               m=self._show_user_collections,
                                               b=self._back,
                                               q=self._quit),
                              books_menu = dict(a=self._add_book,
                                                v=self._view_book,
                                                e=self._edit_book,
                                                d=self._delete_book,
                                                b=self._back),
                              collections_menu = dict(a=self._add_collection,
                                                      v=self._view_collection,
                                                      e=self._edit_collection,
                                                      d=self._delete_collection,
                                                      b=self._back))

    def connection_made(self, transport):
        self._transport = transport

    def data_received(self, raw_data):
        try:
            decoded_data = raw_data.decode('utf-8')
            if self._user is None:
                self._setup_new_user(new_user=decoded_data)
                self._send_formatted_reply(status='OK', command='main_menu', reply='None')
            else:
                self._handle_client_data(decoded_data)
        except UnicodeDecodeError as decode_err:
            self._transport.write(str(decode_err).encode('utf-8'))

    def connection_lost(self, exc, msg='Connection lost, exiting...'):
        self._write(msg)
        self._quit()

    # main menu
    def _show_books(self, client_data, next_menu, status='RE', reply='Empty'):
        if self._bookwarm_server.all_books:
            reply = '\n'.join([book.isbn for book in self._bookwarm_server.all_books])
            next_menu = 'books_menu'
        self._send_formatted_reply(status=status, command=next_menu, reply=reply)


    def _show_user_collections(self, client_data, next_menu,
                               status='RE', reply='You have no collections'):
        if self._user_collections:
            reply = '\n'.join([collection.collection_name
                               for collection in self._user_collections])
            next_menu = 'collections_menu'
        self._send_formatted_reply(status=status, command=next_menu, reply=reply)

    def _quit(self, *ignore):
        self._bookwarm_server.remove_user(self._user)
        self._transport.close()

    # collection handling
    def _add_collection(self, client_data, next_menu, status='RE',
                        reply='Collection created.'):
        self._bookwarm_server.add_new_collection(user=self._user,
                                                 collection_name=client_data)
        self._send_formatted_reply(status=status, command=next_menu, reply=reply)

    def _view_collection(self, *args):
        raise NotImplementedError()

    def _edit_collection(self, *args):
        raise NotImplementedError()

    def _delete_collection(self, *args):
        raise NotImplementedError()

    # book handling
    def _add_book(self, *args):
        raise NotImplementedError()

    def _view_book(self, *args):
        raise NotImplementedError()

    def _edit_book(self, *args):
        raise NotImplementedError()

    def _delete_book(self, *args):
        raise NotImplementedError()

    def _back(self, *args):
        pass

    # supportive methods
    def _handle_client_data(self, decoded_data):
        (command, client_data,
         options_menu, next_client_menu) = decoded_data.split('  ')

        self._commands[options_menu][command](client_data, next_client_menu)

    def _load_user_collections(self):
        self._user_collections = self._bookwarm_server.get_user_collections(self._user)

    def _setup_new_user(self, new_user):
        self._user = new_user
        if not self._bookwarm_server.add_user(self._user):
            self._write('One connection per user allowed.\n'
                        'This client will now exit.')
            self._quit()
        self._load_user_collections()

    def _write(self, text):
        self._transport.write(text.encode('utf-8'))

    def _send_formatted_reply(self, status, command, reply, format='{}  {}  {}'):
        self._write(format.format(status, command, reply))