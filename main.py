from BookStoreServer import BookStoreServer
from BooksStore import BookStore
from Book import Book
import pandas as pd

if __name__ == "__main__":
    #server = BookStoreServer(host="127.0.0.1", port=8574
                             #, genres_lst=["SCI_FI", "NOVEL", "HISTORY", "MANGA", "ROMANCE","PROFESSIONAL"])
    #server.run()


    genres_lst = ["SCI_FI", "NOVEL", "HISTORY", "MANGA", "ROMANCE","PROFESSIONAL"]
    range_of_valid_publication_year = (1940, 2100)
    books_properties = ["id", "title", "author", "price", "year", "genres"]

    book_store = BookStore(genres_lst, range_of_valid_publication_year, books_properties)

    new_book = Book(title="stam", author="dsds", print_year=1950, price=300, genres=["NOVEL"])

    adding_res = book_store.add_book(new_book)
    print(book_store.get_books_data_df())




