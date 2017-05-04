#!/usr/bin/python3


import unittest
import collections
import datetime
import unittest.mock
from bookwarm import Book, UserBook, BookCollection


class TestBook(unittest.TestCase):

    def setUp(self):
        self.user_book_kwargs = dict(isbn=1234567890, title='title',
                                    author='author', genre='genre',
                                    no_of_pages=50, year_published=2017)

    def tearDown(self):
        self.user_book_kwargs.clear()

    def test01_userbook_init_success(self):
        self.assertTrue(UserBook(**self.user_book_kwargs))

    def test02_userbook_init_missing_arg_fail(self):
        del self.user_book_kwargs['isbn']
        with self.assertRaises(TypeError):
            UserBook(**self.user_book_kwargs)

    def test03_userbook_isbn_13_digits_success(self):
        self.user_book_kwargs['isbn'] = 1234567890123
        self.assertTrue(UserBook(**self.user_book_kwargs))

    def test04_userbook_isbn_wrong_digit_number_fail(self):
        self.user_book_kwargs['isbn'] = 12345
        with self.assertRaises(AssertionError):
            self.assertFalse(UserBook(**self.user_book_kwargs))

    def test05_userbook_isbn_wrong_type_fail(self):
        self.user_book_kwargs['isbn'] = 'should be integer'
        with self.assertRaises(AssertionError):
            self.assertFalse(UserBook(**self.user_book_kwargs))

    def test06_userbook_author_too_short_fail(self):
        self.user_book_kwargs['author'] = 'o'
        with self.assertRaises(AssertionError):
            self.assertFalse(UserBook(**self.user_book_kwargs))

    def test07_userbook_author_wrong_type_fail(self):
        self.user_book_kwargs['author'] = 123
        with self.assertRaises(AssertionError):
            self.assertFalse(UserBook(**self.user_book_kwargs))

    def test08_userbook_title_wrong_type_fail(self):
        self.user_book_kwargs['title'] = 'o'
        with self.assertRaises(AssertionError):
            self.assertFalse(UserBook(**self.user_book_kwargs))

    def test09_userbook_title_wrong_type_fail(self):
        self.user_book_kwargs['title'] = 123
        with self.assertRaises(AssertionError):
            self.assertFalse(UserBook(**self.user_book_kwargs))

    def test10_userbook_genre_empty_fail(self):
        self.user_book_kwargs['genre'] = ''
        with self.assertRaises(AssertionError):
            self.assertFalse(UserBook(**self.user_book_kwargs))

    def test11_userbook_genre_wrong_type_fail(self):
        self.user_book_kwargs['genre'] = 123
        with self.assertRaises(AssertionError):
            self.assertFalse(UserBook(**self.user_book_kwargs))

    def test12_userbook_no_of_pages_zero_fail(self):
        self.user_book_kwargs['no_of_pages'] = 0
        with self.assertRaises(AssertionError):
            self.assertFalse(UserBook(**self.user_book_kwargs))

    def test13_userbook_no_of_pages_wrong_type_fail(self):
        self.user_book_kwargs['no_of_pages'] = 'should be int.'
        with self.assertRaises(AssertionError):
            self.assertFalse(UserBook(**self.user_book_kwargs))

    def test14_userbook_year_published_year_exceeded_fail(self):
        self.user_book_kwargs['year_published'] = 2077
        with self.assertRaises(AssertionError):
            self.assertFalse(UserBook(**self.user_book_kwargs))

    def test15_userbook_year_published_wrong_type_fail(self):
        self.user_book_kwargs['year_published'] = 'should be int.'
        with self.assertRaises(AssertionError):
            self.assertFalse(UserBook(**self.user_book_kwargs))

    def test16_userbook_edition_zero_fail(self):
        self.user_book_kwargs['edition'] = 0
        with self.assertRaises(AssertionError):
            self.assertFalse(UserBook(**self.user_book_kwargs))

    def test17_userbook_edition_wrong_type_fail(self):
        self.user_book_kwargs['edition'] = 'should be int.'
        with self.assertRaises(AssertionError):
            self.assertFalse(UserBook(**self.user_book_kwargs))

    def test18_userbook_publisher_empty_success(self):
        self.user_book_kwargs['publisher'] = ''
        self.assertTrue(UserBook(**self.user_book_kwargs))

    def test19_userbook_publisher_wrong_type_fail(self):
        self.user_book_kwargs['publisher'] = 1338
        with self.assertRaises(AssertionError):
            self.assertFalse(UserBook(**self.user_book_kwargs))

    def test20_userbook_notes_default_success(self):
        book = UserBook(**self.user_book_kwargs)
        self.assertEqual(book.notes, [])

    def test21_userbook_notes_not_empty_success(self):
        self.user_book_kwargs['notes'] = ['valid', 'list']
        book = UserBook(**self.user_book_kwargs)
        self.assertEqual(book.notes, ['valid', 'list'])

    def test22_userbook_notes_wrong_type_fail(self):
        self.user_book_kwargs['notes'] = 'not a list'
        with self.assertRaises(AssertionError):
            self.assertFalse(UserBook(**self.user_book_kwargs))

    def test23_userbook_in_collections_default_success(self):
        book = UserBook(**self.user_book_kwargs)
        self.assertEqual(book.in_collections, collections.defaultdict(list))

    def test24_userbook_in_collections_not_empty_success(self):
        non_empty = collections.defaultdict(list)
        non_empty['key'] = ['valid', 'list']
        self.user_book_kwargs['in_collections'] = non_empty
        book = UserBook(**self.user_book_kwargs)
        self.assertEqual(book.in_collections['key'], ['valid', 'list'])

    def test25_userbook_in_collections_wrong_subtype_fail(self):
        non_empty = collections.defaultdict(tuple)
        non_empty['key'] = ('valid', 'list')
        self.user_book_kwargs['in_collections'] = non_empty
        with self.assertRaises(AssertionError):
            self.assertFalse(UserBook(**self.user_book_kwargs))

    def test26_userbook_in_collections_wrong_type_fail(self):
        self.user_book_kwargs['in_collections'] = 'not a defaultdict'
        with self.assertRaises(AssertionError):
            self.assertFalse(UserBook(**self.user_book_kwargs))

    def test27_userbook_tags_default_success(self):
        book = UserBook(**self.user_book_kwargs)
        self.assertEqual(book.tags, set())

    def test28_userbook_tags_not_empty_success(self):
        self.user_book_kwargs['tags'] = set(('valid', 'set'))
        book = UserBook(**self.user_book_kwargs)
        self.assertEqual(book.tags, set(('valid', 'set')))

    def test29_userbook_tags_wrong_type_fail(self):
        self.user_book_kwargs['tags'] = 'not a set'
        with self.assertRaises(AssertionError):
            self.assertFalse(UserBook(**self.user_book_kwargs))

    def test30_userbook_read_default_success(self):
        book = UserBook(**self.user_book_kwargs)
        self.assertEqual(book.read, False)

    def test31_userbook_read_not_empty_success(self):
        self.user_book_kwargs['read'] = True
        book = UserBook(**self.user_book_kwargs)
        self.assertEqual(book.read, True)

    def test32_userbook_read_wrong_type_fail(self):
        self.user_book_kwargs['read'] = 'not a bool'
        with self.assertRaises(AssertionError):
            self.assertFalse(UserBook(**self.user_book_kwargs))

    def test33_userbook_read_date_default_success(self):
        book = UserBook(**self.user_book_kwargs)
        self.assertEqual(book.read_date, datetime.date.min)

    def test34_userbook_read_date_not_empty_success(self):
        self.user_book_kwargs['read_date'] = datetime.date(year=2016, month=3, day=21)
        book = UserBook(**self.user_book_kwargs)
        self.assertEqual(book.read_date, datetime.date(year=2016, month=3, day=21))

    def test35_userbook_read_date_wrong_type_fail(self):
        self.user_book_kwargs['read_date'] = 'not a datetime.date'
        with self.assertRaises(AssertionError):
            self.assertFalse(UserBook(**self.user_book_kwargs))

    def test36_userbook_rating_default_success(self):
        book = UserBook(**self.user_book_kwargs)
        self.assertEqual(book.rating, 0)

    def test37_userbook_rating_not_empty_success(self):
        self.user_book_kwargs['rating'] = 5
        book = UserBook(**self.user_book_kwargs)
        self.assertEqual(book.rating, 5)

    def test38_userbook_rating_exceeded_fail(self):
        self.user_book_kwargs['rating'] = 6
        with self.assertRaises(AssertionError):
            self.assertFalse(UserBook(**self.user_book_kwargs))

    def test39_userbook_rating_wrong_type_fail(self):
        self.user_book_kwargs['rating'] = 'not an int.'
        with self.assertRaises(AssertionError):
            self.assertFalse(UserBook(**self.user_book_kwargs))

    def test40_userbook_add_note_success(self):
        book = UserBook(**self.user_book_kwargs)
        book.add_note('new note')
        self.assertEqual(book.notes, ['new note'])

    def test41_userbook_add_note_empty_fail(self):
        book = UserBook(**self.user_book_kwargs)
        with self.assertRaises(AssertionError):
            self.assertTrue(book.add_note(''))

    def test42_userbook_add_note_wrong_type_fail(self):
        book = UserBook(**self.user_book_kwargs)
        with self.assertRaises(AssertionError):
            self.assertTrue(book.add_note(123))

    def test43_userbook_add_tag_success(self):
        book = UserBook(**self.user_book_kwargs)
        book.add_tag('new tag')
        self.assertEqual(book.tags, {'new tag'})

    def test44_userbook_add_tag_empty_fail(self):
        book = UserBook(**self.user_book_kwargs)
        with self.assertRaises(AssertionError):
            self.assertTrue(book.add_tag(''))

    def test45_userbook_add_tag_wrong_type_fail(self):
        book = UserBook(**self.user_book_kwargs)
        with self.assertRaises(AssertionError):
            self.assertTrue(book.add_tag(123))

    def test46_userbook_add_collection_name_success(self):
        book = UserBook(**self.user_book_kwargs)
        book.add_collection_name('new user', 'new collection')
        self.assertEqual(book.in_collections['new user'], ['new collection'])

    def test47_userbook_add_collection_name_missing_arg_fail(self):
        book = UserBook(**self.user_book_kwargs)
        with self.assertRaises(TypeError):
            book.add_collection_name('new user')

    def test48_userbook_add_collection_name_empty_user_fail(self):
        book = UserBook(**self.user_book_kwargs)
        with self.assertRaises(AssertionError):
            book.add_collection_name('', 'new_collection')

    def test49_userbook_add_collection_name_empty_collection_name_fail(self):
        book = UserBook(**self.user_book_kwargs)
        with self.assertRaises(AssertionError):
            book.add_collection_name('new user', '')

    def test50_userbook_add_collection_wrong_user_type_fail(self):
        book = UserBook(**self.user_book_kwargs)
        with self.assertRaises(AssertionError):
            book.add_collection_name(1337, 'new_collection')

    def test51_userbook_add_collection_wrong_collection_type_fail(self):
        book = UserBook(**self.user_book_kwargs)
        with self.assertRaises(AssertionError):
            book.add_collection_name('new user', 7777)


if __name__ == '__main__':
    unittest.main()