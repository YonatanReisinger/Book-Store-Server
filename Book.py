class Book:

    def __init__(self, title: str, author: str, print_year: int, price: int, genres: list):
        self.title = title
        self.author = author
        self.year = print_year
        self.price = price
        self.genres = genres

    def get_properties(self):
        return self.__dict__



