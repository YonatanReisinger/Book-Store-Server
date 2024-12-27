from PostgresBook import PostgresBook
from MongoBook import MongoBook

class Book:
    books_properties = ["title", "author", "price", "year", "genres"]

    def __init__(self, id: int ,title: str, author: str, print_year: int, price: int, genres: list):
        self.id = id
        self.title = title
        self.author = author
        self.year = print_year
        self.price = price
        self.genres = genres
        self.sql_book = PostgresBook(id, title, author, print_year, price, genres)
        self.mongo_book = MongoBook(id, title, author, print_year, price, genres)

    def get_properties(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'year': self.year,
            'price': self.price,
            'genres': self.genres
        }

    @staticmethod
    def dict_to_book(dictionary: dict):
        if Book.is_dict_a_book(dictionary):
            book = Book(dictionary["title"], dictionary["author"], dictionary["year"]
                        , dictionary["price"], dictionary["genres"])
            return book

    @staticmethod
    def is_dict_a_book(dictionary: dict):
        dict_keys_sorted = sorted(list(dictionary.keys()))
        books_properties_sorted = sorted(Book.books_properties)
        return dict_keys_sorted == books_properties_sorted



