from flask import Flask, request, jsonify
from Book import Book


class BookStoreServer:

    ok_status_code = 200
    conflict_status_code = 409
    not_found_status_code = 404
    bad_request_status_code = 400

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
        app.add_url_rule("/books/total", "books count", self.__books_count, methods=["GET"])
        app.add_url_rule("/books", "books data", self.__books_data, methods=["GET"])
        app.add_url_rule("/book", "book by id", self.__get_book_by_id, methods=["GET"])
        app.add_url_rule("/book", "update_book price", self.__update_book_price, methods=["PUT"])
        app.add_url_rule("/book", "delete book", self.__delete_book_by_id, methods=["DELETE"])


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
            status = BookStoreServer.ok_status_code
        else:
            result = ""
            status = BookStoreServer.conflict_status_code

        response_json = self.__generate_json_response(result, error_message)

        return jsonify(response_json), status

    def __get_filter_requests(self):
        author = request.args.get('author')
        price_bigger_than = request.args.get("price-bigger-than")
        if price_bigger_than is not None:
            price_bigger_than = int(price_bigger_than)
        price_less_than = request.args.get("price-less-than")
        if price_less_than is not None:
            price_less_than = int(price_less_than)
        year_bigger_than = request.args.get("year-bigger-than")
        if year_bigger_than is not None:
            year_bigger_than = int(year_bigger_than)
        year_less_than = request.args.get("year-less-than")
        if year_less_than is not None:
            year_less_than = int(year_less_than)
        genres = request.args.get("genres")
        if genres is not None:
            genres = genres.split(",")

        return (author, price_bigger_than, price_less_than
                , year_bigger_than, year_less_than, genres)

    def __books_count(self):
        filters = self.__get_filter_requests()
        genres = filters[5]

        if genres is None or is_sublist(main_list=self.__book_store.get_genres(), sub_list=genres):
            books_df = self.__book_store.get_books(*filters)
            result = len(books_df)
            status = BookStoreServer.ok_status_code

        else:
            result = ""
            status = BookStoreServer.bad_request_status_code

        return self.__generate_json_response(result, ""), status

    def __books_data(self):
        filters = self.__get_filter_requests()
        genres = filters[5]

        if genres is None or is_sublist(main_list=self.__book_store.get_genres(), sub_list=genres):
            filtered_books_df = self.__book_store.get_books(*filters)
            filtered_books_df = filtered_books_df.sort_values(by='title')
            result = list(filtered_books_df.apply(lambda row: row.to_dict(), axis=1))
            status = BookStoreServer.ok_status_code

        else:
            result = ""
            status = BookStoreServer.bad_request_status_code

        response_json = self.__generate_json_response(result, "")
        return response_json, status

    def __get_book_by_id(self):
        id = int(request.args.get("id"))
        result, book_was_found = self.__book_store.get_book_by_id(id, as_dict=True)
        if book_was_found:
            error_message = ""
            status = BookStoreServer.ok_status_code
        else:
            error_message = f"Error: no such Book with id {id}"
            status = BookStoreServer.not_found_status_code

        return self.__generate_json_response(result, error_message), status

    def __update_book_price(self):
        id = int(request.args.get("id"))
        new_price = int(request.args.get("price"))
        book_series, book_was_found = self.__book_store.get_book_by_id(id, as_dict=False)

        if book_was_found == False:
            result = ""
            error_message = f"Error: no such Book with id {id}"
            status = BookStoreServer.not_found_status_code
        elif new_price <= 0:
            result = ""
            error_message = f"Error: price update for book [{id}] must be a positive integer"
            status = BookStoreServer.conflict_status_code
        else:
            old_price = book_series["price"]
            result = old_price
            self.__book_store.update_book_price(id, new_price)
            error_message = ""
            status = BookStoreServer.ok_status_code

        return self.__generate_json_response(result, error_message), status

    def __delete_book_by_id(self):
        id = int(request.args.get("id"))

        if self.__book_store.is_book_id_in_store(id):
            self.__book_store.remove_book_by_id(id)
            result = self.__book_store.get_num_of_books()
            error_message = ""
            status = BookStoreServer.ok_status_code
        else:
            result = ""
            error_message = f"Error: no such Book with id {id}"
            status = BookStoreServer.not_found_status_code

        return self.__generate_json_response(result, error_message), status

    def __generate_json_response(self, result, error_message):
        response_json = self.__json_response_template
        response_json["result"] = result
        response_json["errorMessage"] = error_message
        return response_json




def is_sublist(main_list: list, sub_list: list) -> bool:
    for element in sub_list:
        if element not in main_list:
            return False
    else:
        return True