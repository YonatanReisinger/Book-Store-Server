from flask import Flask, request, jsonify
from Book import Book

class BookStoreServer:

    def __init__(self, host: str, port: int, book_store):
        self.__app = Flask(__name__)
        self.__host = host
        self.__port = port
        self.__book_store = book_store
        self.__book_store.add_website(self)
        self.setup_routes()
        self.__json_response_template = {"errorMessage": "", "result": ""}

    def run(self):
        self.__app.run(self.__host, self.__port)

    def setup_routes(self):
        app = self.__app
        app.add_url_rule("/", "index", self.__index)
        app.add_url_rule("/books/health", "health", self.__health, methods=["GET"])
        app.add_url_rule("/book", "create", self.__add_book, methods=["POST"])
        app.add_url_rule("/book/total", "books count", self.__books_count, methods=["GET"])

    def __index(self):
        return "Hello World"

    def __health(self):
        return "OK"

    def __add_book(self):
        new_book_dict = request.get_json()
        new_book = Book.dict_to_book(new_book_dict)

        error_message = self.__book_store.add_book(new_book)
        if error_message == "":
            result = self.__book_store.get_num_of_books() # The new ID is the number of books after the adding
            status = 200
        else:
            result = ""
            status = 409

        response_json = self.__generate_json_response(result, error_message)

        return jsonify(response_json), status

    def __books_count(self):
        author = request.args.get('author')  # Retrieve the 'author' query parameter
        price_bigger_than = request.args.get("price_bigger_than")
        price_less_than = request.args.get("price_less_than")
        year_bigger_than = request.args.get("year_bigger_than")
        year_less_than = request.args.get("year_less_than")
        genres = request.args.get("genres")

        result = self.__book_store.get_books_count(author, price_bigger_than, price_less_than
                                                   , year_bigger_than, year_less_than, genres)

        return "super"

    def __generate_json_response(self, result, error_message):
        response_json = self.__json_response_template
        response_json["result"] = result
        response_json["errorMessage"] = error_message
        return response_json


