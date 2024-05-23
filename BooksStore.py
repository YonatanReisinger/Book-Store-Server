import pandas as pd
from Book import Book

class BookStore:


    def __init__(self, genres_lst: list, range_of_valid_print_years: tuple, books_properties: list):
        self.__genres = list()
        self.__range_of_valid_print_years = tuple()
        self.__books_properties = list()
        self.__id_for_next_book = 1

        self.set_genres(genres_lst)
        self.set_range_of_valid_publication_year(range_of_valid_print_years)
        self.set_books_properties(books_properties)

        self.__books_data = pd.DataFrame(columns=books_properties)
        self.__online_store_server = None

    # --------------------- State Changers ---------------------

    def add_book(self, new_book: Book) -> str:
        if self.is_book_in_store(new_book):
            book_title_in_store = new_book.title.lower()
            error_message = f"Error: Book with the title [{book_title_in_store}] already exists in the system"

        elif self.is_book_print_year_in_range(new_book) == False:

            error_message = (f"Error: Can’t create new Book that its year [{new_book.year}] "
                             f"is not in the accepted range [{self.__range_of_valid_print_years[0]} -> {self.__range_of_valid_print_years[1]}]")

        elif new_book.price <= 0:
            error_message = "Error: Can’t create new Book with negative price"

        else:
            new_book_id = self.__id_for_next_book
            self.__id_for_next_book += 1
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

    def add_website(self, server):
        self.__online_store_server = server

    def update_book_price(self, id: int, new_price: int):
        if new_price > 0:
            self.__books_data.loc[self.__books_data['id'] == id, 'price'] = new_price

    def remove_book_by_id(self, id: int):
        if self.is_book_id_in_store(id):
            condition = self.__books_data['id'] != id
            self.__books_data = self.__books_data[condition]

    # --------------------- Queries ---------------------

    def is_book_id_in_store(self, id: int):
        return id in self.__books_data["id"].values

    def is_book_in_store(self, book: Book):
        book_title_in_store = book.title.lower()
        return book_title_in_store in self.__books_data["title"].values

    def is_book_print_year_in_range(self, book: Book):
        return self.__range_of_valid_print_years[0] <= book.year <= self.__range_of_valid_print_years[1]

    def is_genre_in_store(self, genre: str):
        return genre in self.__genres

    def get_books(self, author: str = None, price_bigger_than: int = None, price_less_than: int = None
                        , year_bigger_than: int = None, year_less_than: int = None, genres: list = None):

        params = [author, price_bigger_than, price_less_than, year_bigger_than, year_less_than, genres]

        condition_author = self.__books_data["author"] == author
        condition_price_bigger_than = self.__books_data["price"] >= price_bigger_than
        condition_price_less_than = self.__books_data["price"] <= price_less_than
        condition_year_bigger_than = self.__books_data["year"] >= year_bigger_than
        condition_year_less_than = self.__books_data["year"] <= year_less_than
        condition_genres = self.__books_data["genres"].apply(lambda book_genres: genres is not None and not set(genres).isdisjoint(book_genres))

        all_conditions = [condition_author, condition_price_bigger_than, condition_price_less_than
                          , condition_year_bigger_than, condition_year_less_than, condition_genres]
        requested_conditions = []
        for i in range(len(params)):
            if params[i] is not None:
                requested_conditions.append(all_conditions[i])

        if len(requested_conditions) == 0:
            return self.__books_data
        else:
            # Combine all conditions using the AND operator
            combined_requested_conditions = requested_conditions[0]
            for condition in requested_conditions[1:]:
                combined_requested_conditions &= condition

            return self.__books_data[combined_requested_conditions]

    def get_book_by_id(self, id: int, as_dict=False):
        books_df = self.__books_data
        condition = books_df["id"] == id
        book_with_id_df = books_df[condition]
        if book_with_id_df.empty:
            return {}, False
        elif as_dict is True:
            return book_with_id_df.iloc[0].to_dict(), True
        else:
            return book_with_id_df.iloc[0], True

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

    def get_num_of_books(self):
        return len(self.__books_data)

    def get_genres(self):
        return list(self.__genres)


