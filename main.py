from BookStoreServer import BookStoreServer
from BooksStore import BookStore

if __name__ == "__main__":

    genres_lst = ["SCI_FI", "NOVEL", "HISTORY", "MANGA", "ROMANCE","PROFESSIONAL"]
    range_of_valid_publication_year = (1940, 2100)
    books_properties = ["id", "title", "author", "price", "year", "genres"]

    book_store = BookStore(genres_lst, range_of_valid_publication_year, books_properties)

    server = BookStoreServer(host="127.0.0.1", port=8574, book_store=book_store)
    server.run()




