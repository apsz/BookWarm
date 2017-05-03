#!/usr/bin/python3


import datetime
from bookwarm import Book, UserBook, BookCollection


test_user_book = UserBook(1234567890, 'Hello',
                'Misa', 'qwww', 5, 2017)
test_user_book2 = UserBook(1234567891, 'Hello',
                'Misa', 'qwww', 5, 2017)
books_coll = BookCollection({})
books_coll[test_user_book.isbn] = test_user_book
books_coll[test_user_book2.isbn] = test_user_book2
del books_coll[test_user_book2.isbn]
print(books_coll)
