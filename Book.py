class Book:
    books_properties = ["title", "author", "price", "year", "genres"]

    def __init__(self, title: str, author: str, print_year: int, price: int, genres: list):
        self.title = title
        self.author = author
        self.year = print_year
        self.price = price
        self.genres = genres

    def get_properties(self):
        return self.__dict__

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



