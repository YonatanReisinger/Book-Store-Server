import pandas as pd
from BookStoreServer import BookStoreServer
from Book import Book

class BookStore:


    def __init__(self, genres_lst: list, range_of_valid_print_years: tuple, books_properties: list, online_store_ip="127.0.0.1", online_store_port=8574):
        self.__genres = list()
        self.__range_of_valid_print_years = tuple()
        self.__books_properties = list()
        self.__num_of_books = 0

        self.set_genres(genres_lst)
        self.set_range_of_valid_publication_year(range_of_valid_print_years)
        self.set_books_properties(books_properties)

        self.__books_data = pd.DataFrame(columns=books_properties)
        self.__online_store_server = BookStoreServer(host=online_store_ip, port=online_store_port)

    # --------------------- State Changers ---------------------

    def add_book(self, new_book: Book) -> str:
        if self.is_book_in_store(new_book):
            book_title_in_store = new_book.title.lower()
            error_message = f"Error: Book with the title [{book_title_in_store}] already exists in the system"

        elif self.is_book_print_year_in_range(new_book) == False:

            error_message = (f"Error: Can’t create new Book that its year [{new_book.print_year}] "
                             f"is not in the accepted range [{self.__range_of_valid_print_years[0]} -> {self.__range_of_valid_print_years[1]}]")

        elif new_book.price <= 0:
            error_message = "Error: Can’t create new Book with negative price"

        else:
            self.__num_of_books += 1
            new_book_id = self.__num_of_books
            new_book_properties = new_book.get_properties()
            new_book_properties_in_store = {"id": new_book_id}
            # Add existing key-value pairs to the new dictionary
            for key, value in new_book_properties.items():
                new_book_properties_in_store[key] = value
            book_title_in_store = new_book.title.lower()
            new_book_properties_in_store["title"] = book_title_in_store
            self.__books_data = self.__books_data._append(new_book_properties_in_store, ignore_index=True)
            error_message = ""

        return error_message

    # --------------------- Queries ---------------------
    def is_book_in_store(self, book: Book):
        book_title_in_store = book.title.lower()
        return book_title_in_store in self.__books_data["title"].values

    def is_book_print_year_in_range(self, book: Book):
        return self.__range_of_valid_print_years[0] <= book.year <= self.__range_of_valid_print_years[1]

    # --------------------- Setters ---------------------
    def set_genres(self, genres_lst: list):
        if all(isinstance(genre, str) for genre in genres_lst):
            self.__genres = genres_lst
        else:
            raise ValueError("All genres must be strings.")

    def set_range_of_valid_publication_year(self, range_of_valid_print_years: tuple):
        if (not isinstance(range_of_valid_print_years, tuple) or
                len(range_of_valid_print_years) != 2 or
                not all(isinstance(year, int) for year in range_of_valid_print_years)):
            raise ValueError("range_of_valid_publication_year must be a tuple of two integers.")
        else:
            self.__range_of_valid_print_years = range_of_valid_print_years

    def set_books_properties(self, books_properties: list):
        if all(isinstance(prop, str) for prop in books_properties):
            self.__books_properties = books_properties
        else:
            raise ValueError("All books in store properties must be strings.")

    # --------------------- Getters ---------------------

    def get_books_data_df(self):
        return self.__books_data


