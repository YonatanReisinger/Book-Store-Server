import pandas as pd

from BookStoreServer import BookStoreServer
from BooksStore import BookStore
from Book import Book

if __name__ == "__main__":

    genres_lst = ["SCI_FI", "NOVEL", "HISTORY", "MANGA", "ROMANCE","PROFESSIONAL"]
    range_of_valid_publication_year = (1940, 2100)
    books_properties = ["id", "title", "author", "price", "year", "genres"]

    book_store = BookStore(genres_lst, range_of_valid_publication_year, books_properties)

    new_book = Book("stam", "dsds", 1950, 300, ["NOVEL"])
    new_book2 = Book("sefher", "yon", 1960, 400, ["NOVEL", "HISTORY"])
    new_book3 = Book("tovvv", "jon", 1970, 500, ["ROMANCE", "PROFESSIONAL"])

    book_store.add_book(new_book)
    book_store.add_book(new_book2)
    book_store.add_book(new_book3)

    server = BookStoreServer(host="127.0.0.1", port=8574, book_store=book_store)
    server.run()




