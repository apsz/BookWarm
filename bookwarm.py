#!/usr/bin/python3
# TODO: BookCollection
# TODO:  - export (to xml, text)
# TODO:  - import (from xml, text)
# TODO:  - filter by any attr
# TODO:  - subclass of dict => custom
# TODO: Client
# TODO:  - request collections as necessary and cache them
# TODO: Server
# TODO:  - store available books separately in a binary file
# TODO:  - store each collection separately in a binary file
# TODO:  - asyncio to handle requests


import os
import pyparsing
import datetime
import operator
import collections


class Book:

    def __init__(self, isbn, title, author, genre, no_of_pages,
                 year_published, edition=1, publisher=''):
        assert isinstance(isbn, int) and (len(str(isbn)) == 10 or len(str(isbn)) == 13), (
            'ISBN must be non-empty integer of 10 or 13 digits.')
        self.__isbn = isbn
        assert isinstance(title, str) and len(title) > 2, (
            'title must be non-empty string of at least 2 characters.')
        self.__title = title
        assert isinstance(author, str) and len(author) > 2, (
            'author must be non-empty string of at least 2 characters.')
        self.__author = author
        self.genre = genre
        self.no_of_pages = no_of_pages
        self.edition = edition
        self.year_published = year_published
        self.publisher = publisher

    @property
    def isbn(self):
        return self.__isbn

    @property
    def title(self):
        return self.__title

    @property
    def author(self):
        return self.__author

    @property
    def no_of_pages(self):
        return self.__no_of_pages

    @no_of_pages.setter
    def no_of_pages(self, new_number):
        assert isinstance(new_number, int) and new_number > 0, (
            'Must be non-zero integer value.')
        self.__no_of_pages = new_number

    @property
    def year_published(self):
        return self.__year_published

    @year_published.setter
    def year_published(self, new_year):
        assert isinstance(new_year, int) and new_year <= datetime.date.today().year, (
            'Must be integer =< {}'.format(datetime.date.today().year))
        self.__year_published = new_year

    @property
    def edition(self):
        return self.__edition

    @edition.setter
    def edition(self, new_edition):
        assert isinstance(new_edition, int) and new_edition > 0, (
            'Must be non-zero integer value.')
        self.__edition = new_edition

    @property
    def publisher(self):
        return self.__publisher

    @publisher.setter
    def publisher(self, new_publisher):
        assert isinstance(new_publisher, str), 'Must be string value.'
        self.__publisher = new_publisher


class UserBook(Book):

    def __init__(self, isbn, title, author, genre, no_of_pages,
                 year_published, edition=1, publisher='',
                 notes=None, read=False, read_date=datetime.date.min, rating=0,
                 in_user_collections=None, tags=None):
        super().__init__(isbn, title, author, genre, no_of_pages,
                         year_published, edition, publisher)
        self.notes = notes or []
        self.in_collections = in_user_collections or collections.defaultdict(list)
        self.tags = tags or set()
        self.read = read
        self.read_date = read_date
        self.rating = rating

    @property
    def notes(self):
        return self.__notes

    @notes.setter
    def notes(self, new_notes):
        assert isinstance(new_notes, list), 'Must be a list class.'
        self.__notes = new_notes

    @property
    def in_user_collections(self):
        return self.__in_user_collections

    @in_user_collections.setter
    def in_user_collections(self, new_in_collections):
        assert isinstance(new_in_collections, collections.defaultdict), (
            'Must be a defaultdict class.')
        assert all(isinstance(element, list) for element in new_in_collections.values()), (
            'Each value has to be list class.')
        self.__in_user_collections = new_in_collections

    @property
    def read(self):
        return self.__read

    @read.setter
    def read(self, read_state):
        assert isinstance(read_state, bool), 'Must be True/False.'
        self.__read = read_state

    @property
    def read_date(self):
        return self.__read_date

    @read_date.setter
    def read_date(self, new_read_date):
        assert isinstance(new_read_date, datetime.date), 'Must be datetime.date class.'
        self.__read_date = new_read_date

    @property
    def rating(self):
        return self.__rating

    @rating.setter
    def rating(self, new_rating):
        assert isinstance(new_rating, int) and 0 <= new_rating <= 5, (
            'Must be integer between 0 and 5.')
        self.__rating = new_rating

    @property
    def tags(self):
        return self.__tags

    @tags.setter
    def tags(self, new_tags):
        assert isinstance(new_tags, set), 'Must be a set class.'
        self.__tags = new_tags

    def add_note(self, note):
        assert isinstance(note, str), 'Must be a string.'
        self.notes.append(note)

    def add_collection_name(self, user, user_collection_name):
        assert isinstance(user_collection_name, str) and isinstance(user, str), (
            'Must be a string.')
        self.in_user_collections[user].append(user_collection_name)

    def add_tag(self, tag_to_add):
        assert isinstance(tag_to_add, str), 'Must be a string.'
        self.tags.add(tag_to_add)


def delegate_methods(attribute_name, method_names):
    def decorator(cls):
        nonlocal attribute_name
        if attribute_name.startswith('__'):
            attribute_name = '_{}__{}'.format(cls.__name__,
                                              attribute_name[2:])
            for method in method_names:
                setattr(cls, method, eval('lambda self, *args, **kwargs: '
                                          'self.{}.{}(*args, **kwargs)'.format(
                                           attribute_name, method)))
        return cls
    return decorator


@delegate_methods('__book_collection', ('pop', '__getitem__', '__delitem__',
                                        '__len__', '__str__', '__repr__',
                                        '__values__', '__items__'))
class BookCollection:

    available_filters = ('isbn', 'title', 'author', 'genre', 'year_published',
                         'edition', 'publisher')

    def __init__(self, user, collection_name, book_collection):
        self.user = user
        self.collection_name = collection_name
        self.__book_collection = {}
        if book_collection:
            assert all(isinstance(element, Book) for element in book_collection), (
                'Each item of book_collection has to be Book class')
            self.__book_collection = book_collection

    def __setitem__(self, isbn, book_instance):
        assert isinstance(book_instance, Book), 'Must be Book class.'
        assert isinstance(isbn, int) and (len(str(isbn)) == 10 or len(str(isbn)) == 13), (
            'ISBN must be non-empty integer of 10 or 13 digits.')
        self.__book_collection[isbn] = book_instance

    def __iter__(self):
        for isbn in sorted(self.__book_collection):
            yield isbn

    keys = __iter__

    def values(self):
        for book_instance in self.__book_collection.values():
            yield book_instance

    def items(self):
        for isbn in self.__book_collection:
            yield (isbn, self.__book_collection[isbn])

    def filter(self, key):
        if key not in BookCollection.available_filters:
            raise KeyError('Valid filters: {}'.format(
                ' '.join(BookCollection.available_filters)))
        return sorted(self.__book_collection.values(), key=operator.attrgetter(key))

    def save_as_text(self):
        filename = '{} {}.txt'.format(self.user, self.collection_name)
        fullpath_to_save = os.path.join(os.path.dirname(__file__), filename)
        try:
            with open(fullpath_to_save, 'w') as fh:
                for book in self.__book_collection.values():
                    in_collections = ''
                    for user in book.in_collections:
                        in_collections += '  {}: {}'.format(
                            user, ','.join(collection_name
                                           for collection_name in book.in_collections[user]))
                    fh.write('[{0.isbn}]\n'
                             '\ttitle={0.title}\n'
                             '\tauthor={0.author}\n'
                             '\tgenre={0.genre}\n'
                             '\tyear_published={0.year_published}\n'
                             '\tedition={0.edition}\n'
                             '\tpublisher={0.publisher}\n'
                             '\tread={0.read}\n'
                             '\tread_date={0.read_date}\n'
                             '\trating={0.rating}\n'
                             '\ttags={tags}\n'
                             '\tin_collections={in_collections}\n'
                             '\tNOTES>\n'
                             '\t\t{notes}\n'
                             '\t<NOTES\n\n'.format(book,
                                                      tags=' '.join(book.tags),
                                                      in_collections=in_collections.strip(),
                                                      notes='\n\t\t'.join(('{}'.format(line)
                                                                           for line in book.notes))))
            return True
        except (EnvironmentError, IOError, UnicodeError) as save_err:
            print('Error while saving collection {}: {}'.format(self.collection_name,
                                                                save_err))
            return False

    def load_from_text(self):
        pass





