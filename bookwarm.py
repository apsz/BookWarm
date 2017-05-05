#!/usr/bin/python3
# TODO: BookCollection
# TODO: tests
# TODO: structure
# TODO: Client
# TODO:  - request collections as necessary and cache them
# TODO: Server
# TODO:  - store available books separately in a binary file
# TODO:  - store each collection separately in a binary file
# TODO:  - asyncio to handle requests


import os
import sys
import operator
import collections
import datetime
import xml.etree.ElementTree
import xml.parsers.expat
from pyparsing import (Suppress, Word, OneOrMore, ParseException, Regex,
                       restOfLine, ZeroOrMore, alphas, nums)


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
    def genre(self):
        return self.__genre

    @genre.setter
    def genre(self, new_genre):
        assert isinstance(new_genre, str) and len(new_genre) > 1, (
            'Must be a non-empty string.')
        self.__genre = new_genre

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
                 in_collections=None, tags=None):
        super().__init__(isbn, title, author, genre, no_of_pages,
                         year_published, edition, publisher)
        self.notes = notes or []
        self.in_collections = in_collections or collections.defaultdict(list)
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
    def in_collections(self):
        return self.__in_collections

    @in_collections.setter
    def in_collections(self, new_in_collections):
        assert isinstance(new_in_collections, collections.defaultdict), (
            'Must be a defaultdict class.')
        assert all(isinstance(element, list) for element in new_in_collections.values()), (
            'Each value has to be list class.')
        self.__in_collections = new_in_collections

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

    def add_note(self, new_note):
        assert isinstance(new_note, str) and len(new_note) > 1, (
            'Must be a non-empty string.')
        self.notes.append(new_note)

    def add_collection_name(self, user, user_collection_name):
        assert (isinstance(user_collection_name, str) and isinstance(user, str)
            and len(user) > 1) and len(user_collection_name) > 1, ('Must be a non-empty string.')
        self.in_collections[user].append(user_collection_name)

    def add_tag(self, tag_to_add):
        assert isinstance(tag_to_add, str) and len(tag_to_add) > 1, (
            'Must be a non-empty string.')
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
    book_attribute_names = ('isbn', 'title', 'author', 'genre', 'no_of_pages',
                            'year_published', 'edition', 'publisher', 'read',
                            'read_date', 'rating', 'tags', 'in_collections', 'notes')

    def __init__(self, user, collection_name, book_collection):
        assert isinstance(user, str) and len(user) > 1, (
            'Must be a non-empty string')
        self.user = user
        assert isinstance(collection_name, str) and len(collection_name) > 1, (
            'Must be a non-empty string')
        self.collection_name = collection_name
        self.__book_collection = {}
        if book_collection:
            assert isinstance(book_collection, dict), 'Must be a dict class.'
            assert all(isinstance(element, Book) for element in book_collection.values()), (
                'Each item of book_collection has to be Book (sub)class')
            self.__book_collection = book_collection

    def __setitem__(self, isbn, book_instance):
        assert isinstance(book_instance, Book), 'Must be Book (sub)class.'
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

    def save_to_text(self):
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
                             '\tno_of_pages={0.no_of_pages}\n'
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

    def _parse_text(self, text):

        """ BNF


            BOOK         ::=        BOOK_ISBN \s* ATTR_LIST \s* NOTES 
            NOTES        ::=        'NOTES>' NOTES_VALUES '<NOTES'
            NOTES_VALUES ::=        TEXT 
                                    | TEXT \s* NOTES_VALUES
            ATTR_LIST    ::=        ATTR 
                                    | ATTR \s* ATTR_LIST
            ATTR         ::=        KEY \s* = \s* VALUE
            VALUE        ::=        TEXT 
                                    | INT
                                    | DATE
            BOOK_ISBN    ::=        '[' INT ']'
            KEY          ::=        [a-zA-Z_]+
            INT          ::=        \d+
            TEXT         ::=        [^\s]+
            DATE         ::=        \d{4}-\d{2}-\d{2} 

        """

        def set_book_key(tokens):
            nonlocal current_key
            current_key = tokens.isbn[0]
            parsed_books[current_key]['isbn'] = int(current_key)

        def get_in_collection_value(key, value):
            in_collections = {}
            items = value.split('  ')
            for item in items:
                user, collection_names = item.split(':')
                in_collections[user] = (collection_names.strip().split(',')
                                        if ',' in collection_names else [collection_names.strip()])
            return in_collections

        def add_book_attr(tokens):
            key, value = tokens[0].strip(), tokens[1].strip()
            if key == 'in_collections' and tokens[1]:
                value = get_in_collection_value(key, tokens[1])
            if key in frozenset(('year_published', 'no_of_pages', 'edition', 'rating')):
                value = int(value)
            if key == 'read_date':
                value = datetime.datetime.strptime(value, '%Y-%m-%d')
            if key == 'read':
                value = bool(value)
            parsed_books[current_key][key] = value

        def add_notes(tokens):
            parsed_books[current_key]['notes'] = list(tokens)

        parsed_books = collections.defaultdict(dict)
        current_key = ''

        r_bracket, l_bracket, equals, r_arrow, l_arrow = map(Suppress, '][=><')
        book_start = (l_bracket + Word(nums) + r_bracket)('isbn')
        book_start.addParseAction(set_book_key)
        key = Word(alphas + '_')
        value = restOfLine()
        key_value = key + equals + value
        key_value.addParseAction(add_book_attr)
        notes_identifier = Suppress('NOTES')
        notes_text = ZeroOrMore(Regex(r'\w+'))
        notes = notes_identifier + r_arrow + notes_text + l_arrow + notes_identifier
        notes.addParseAction(add_notes)
        book = book_start + OneOrMore(key_value) + notes
        books = OneOrMore(book)

        try:
            books.parseString(text, parseAll=True)
            return parsed_books
        except ParseException as parse_err:
            print('Error: {}'.format(parse_err))
            return []

    def load_from_text(self):
        filename = '{} {}.txt'.format(self.user, self.collection_name)
        fullpath_to_load = os.path.join(os.path.dirname(__file__), filename)
        try:
            with open(fullpath_to_load) as fh:
                source_file_text = fh.read()
        except (EnvironmentError, IOError) as load_err:
            print('Error while loading collection {}: {}'.format(self.collection_name,
                                                                 load_err))
            return False

        book_collection = {}
        books = self._parse_text(source_file_text)
        if not books:
            return False
        for isbn in books.keys():
            book_collection[isbn] = books[isbn]
        self.__book_collection.clear()
        self.__book_collection.update(book_collection)
        return True

    def save_to_xml(self):

        def prepare_in_collections(book):
            in_collections_str = ''
            for user in book.in_collections:
                in_collections_str += '  {}: {}'.format(
                    user, ','.join(collection_name.strip()
                                   for collection_name in book.in_collections[user]))
            return in_collections

        filename = '{} {}.xml'.format(self.user, self.collection_name)
        fullpath_to_save = os.path.join(os.path.dirname(__file__), filename)

        root = xml.etree.ElementTree.Element('books')
        for book in self.__book_collection.values():
            main_book = xml.etree.ElementTree.Element('book')
            for attr in BookCollection.book_attribute_names[:-3]:
                sub_element = xml.etree.ElementTree.SubElement(main_book, attr)
                sub_element.text = str(getattr(book, attr))
            tags = xml.etree.ElementTree.SubElement(main_book, 'tags')
            tags.text = ' '.join(book.tags)
            in_collections = xml.etree.ElementTree.SubElement(main_book, 'in_collections')
            in_collections.text = prepare_in_collections(book)
            notes = xml.etree.ElementTree.SubElement(main_book, 'notes')
            notes.text = '  '.join(('{}'.format(line) for line in book.notes))
            root.append(main_book)

        tree = xml.etree.ElementTree.ElementTree(root)
        try:
            tree.write(fullpath_to_save, 'UTF-8')
            return True
        except (IOError, EnvironmentError, xml.parsers.expat.ExpatError) as export_err:
            print('{} error: {}'.format(os.path.basename(sys.argv[0]), export_err))
            return False

    def load_from_xml(self):

        def get_in_collections_value(key, value):
            in_collections = collections.defaultdict(list)
            if not value:
                return in_collections
            items = value.split('  ')
            for item in items:
                user, collection_names = item.split(':')
                in_collections[user] = (collection_names.strip().split(',')
                                        if ',' in collection_names else [collection_names.strip()])
            return in_collections

        filename = '{} {}.xml'.format(self.user, self.collection_name)
        fullpath_to_load = os.path.join(os.path.dirname(__file__), filename)
        try:
            data = xml.etree.ElementTree.parse(fullpath_to_load)
        except (IOError, EnvironmentError, xml.parsers.expat.ExpatError) as import_err:
            print('{} import error: {}'.format(os.path.basename(sys.argv[0]), import_err))
            return False

        new_books = {}
        try:
            for book in data.findall('book'):
                new_book = {}
                for attr in BookCollection.book_attribute_names:
                    new_book[attr] = book.find(attr).text or ''
                for int_attr in ('isbn', 'no_of_pages', 'year_published',
                                 'edition', 'rating'):
                    new_book[int_attr] = int(new_book[int_attr])
                new_book['read'] = bool(new_book['read'])
                new_book['read_date'] = datetime.datetime.strptime(new_book['read_date'], '%Y-%m-%d')
                tags_text = book.find('tags').text
                new_book['tags'] = set(tags_text.split()) if tags_text else set()
                new_book['in_collections'] = get_in_collections_value('in_collections',
                                                                      book.find('in_collections').text)
                notes_text = book.find('notes').text
                new_book['notes'] = notes_text.split('  ') if notes_text else  []
                book_to_add = UserBook(**new_book)
                new_books[book_to_add.isbn] = book_to_add
        except (ValueError, TypeError, LookupError) as import_err:
            print('{} import error: {}'.format(os.path.basename(sys.argv[0]), import_err))
            return False
        else:
            self.__book_collection.clear()
            self.__book_collection.update(new_books)
            return True







