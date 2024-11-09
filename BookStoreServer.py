from flask import Flask, request, jsonify
from Book import Book
import logging
import time
import os

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
        self.__request_logger = None
        self.__books_logger = None
        self.__current_request = None
        self.__current_request_num = 0
        self.__setup_loggers()

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
        app.add_url_rule("/logs/level", "get log level", self.__get_logger_level, methods=["GET"])
        app.add_url_rule("/logs/level", "set log level", self.__set_logger_level, methods=["PUT"])

    def __setup_loggers(self):
        # Create the logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
        # Disable Flask's logger
        self.__app.logger.handlers.clear()
        log = logging.getLogger('werkzeug')
        log.disabled = True

        self.__setup_request_logger(logging.INFO)
        self.__setup_books_logger(logging.INFO)

    def __setup_request_logger(self, default_level):
        self.__request_logger = logging.getLogger('request-logger')
        self.__request_logger.propagate = False
        self.__request_logger.setLevel(default_level)
        # Create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s: %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
        # Create file handler for logging to a file
        file_handler = logging.FileHandler('logs/requests.log')
        file_handler.setLevel(default_level)
        file_handler.setFormatter(formatter)
        # Create console handler for logging to a file
        console_handler = logging.StreamHandler()
        console_handler.setLevel(default_level)
        console_handler.setFormatter(formatter)
        # Add handlers to the logger
        self.__request_logger.addHandler(console_handler)
        self.__request_logger.addHandler(file_handler)
        # Do the following before and after each request
        self.__app.before_request(self.__log_request)
        self.__app.after_request(self.__log_duration)

    def __log_request(self):
        self.__current_request = request
        self.__current_request_num += 1
        self.__current_request.start_time = time.time()
        self.__request_logger.info(f"Incoming request | #{ self.__current_request_num} | resource: { self.__current_request.path} | HTTP Verb {self.__current_request.method} | request #{self.__current_request_num}")

    def __log_duration(self, response):
        duration = (time.time() - self.__current_request.start_time) * 1000  # convert to milliseconds
        self.__request_logger.debug(f"request #{self.__current_request_num} duration: {duration:.5f}ms | request #{self.__current_request_num}")
        return response

    def __setup_books_logger(self, default_level):
        self.__books_logger = logging.getLogger('books-logger')
        self.__books_logger.propagate = False
        self.__books_logger.setLevel(default_level)
        # Create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s: %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
        # Create file handler for logging to a file
        file_handler = logging.FileHandler('logs/books.log')
        file_handler.setLevel(default_level)
        file_handler.setFormatter(formatter)
        self.__books_logger.addHandler(file_handler)

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
            self.__log_info_add_book(new_book.title)
            self.__log_debug_add_book()
        else:
            result = ""
            status = BookStoreServer.conflict_status_code
            self.__books_logger.error(error_message)

        response_json = self.__generate_json_response(result, error_message)
        return jsonify(response_json), status

    def __log_info_add_book(self, new_book_title):
        self.__books_logger.info(f"Creating new Book with Title [{new_book_title}] | request #{self.__current_request_num}")

    def __log_debug_add_book(self):
        num_of_books_after_adding = self.__book_store.get_num_of_books()
        self.__books_logger.debug(f"Currently there are {num_of_books_after_adding-1} Books in the system. New Book will be assigned with id {num_of_books_after_adding} | request #{self.__current_request_num}")

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
            genres = genres.replace(" ", "")
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
            self.__log_info_books_data(result)
        else:
            result = ""
            status = BookStoreServer.bad_request_status_code

        return self.__generate_json_response(result, ""), status

    def __books_data(self):
        filters = self.__get_filter_requests()
        genres = filters[5]

        if genres is None or is_sublist(main_list=self.__book_store.get_genres(), sub_list=genres):
            filtered_books_df = self.__book_store.get_books(*filters)
            # Convert 'title' column to lowercase for case-insensitive sorting
            filtered_books_df['title_lower'] = filtered_books_df['title'].str.lower()
            filtered_books_df = filtered_books_df.sort_values(by='title_lower')
            # Drop the temporary lowercase title column
            filtered_books_df.drop(columns=['title_lower'], inplace=True)
            result = list(filtered_books_df.apply(lambda row: row.to_dict(), axis=1))
            status = BookStoreServer.ok_status_code
            self.__log_info_books_data(len(result))
        else:
            result = ""
            status = BookStoreServer.bad_request_status_code

        response_json = self.__generate_json_response(result, "")
        return response_json, status

    def __log_info_books_data(self, total_books_found):
        self.__books_logger.info(f"Total Books found for requested filters is {total_books_found} | request #{self.__current_request_num}")

    def __get_book_by_id(self):
        id = int(request.args.get("id"))
        result, book_was_found = self.__book_store.get_book_by_id(id, as_dict=True)
        if book_was_found:
            error_message = ""
            status = BookStoreServer.ok_status_code
            self.__log_debug_get_book_by_id(id)
        else:
            error_message = f"Error: no such Book with id {id}"
            status = BookStoreServer.not_found_status_code
            self.__books_logger.error(error_message)

        return self.__generate_json_response(result, error_message), status

    def __log_debug_get_book_by_id(self, id):
        self.__books_logger.debug(f"Fetching book id {id} details | request #{self.__current_request_num}")

    def __update_book_price(self):
        id = int(request.args.get("id"))
        new_price = int(request.args.get("price"))
        book_series, book_was_found = self.__book_store.get_book_by_id(id, as_dict=False)

        if book_was_found == False:
            result = ""
            error_message = f"Error: no such Book with id {id}"
            status = BookStoreServer.not_found_status_code
            self.__books_logger.error(error_message)
        elif new_price <= 0:
            result = ""
            error_message = f"Error: price update for book [{id}] must be a positive integer"
            status = BookStoreServer.conflict_status_code
            self.__books_logger.error(error_message)
        else:
            old_price = book_series["price"]
            result = old_price
            self.__book_store.update_book_price(id, new_price)
            error_message = ""
            status = BookStoreServer.ok_status_code
            self.__log_info_update_book_price(id, new_price)
            self.__log_debug_update_book_price(book_series["title"], old_price, new_price)

        return self.__generate_json_response(result, error_message), status

    def __log_info_update_book_price(self, id, new_price):
        self.__books_logger.info(f"Update Book id [{id}] price to {new_price} | request #{self.__current_request_num}")

    def __log_debug_update_book_price(self, book_title, old_price, new_price):
        self.__books_logger.debug(f"Book [{book_title}] price change: {old_price} --> {new_price} | request #{self.__current_request_num}")

    def __delete_book_by_id(self):
        id = int(request.args.get("id"))

        if self.__book_store.is_book_id_in_store(id):
            removed_book_title = self.__book_store.get_book_by_id(id)[0]["title"]
            self.__book_store.remove_book_by_id(id)
            result = self.__book_store.get_num_of_books()
            error_message = ""
            status = BookStoreServer.ok_status_code
            self.__log_info_delete_book(removed_book_title)
            self.__log_debug_delete_book(removed_book_title, id, self.__book_store.get_num_of_books())
        else:
            result = ""
            error_message = f"Error: no such Book with id {id}"
            status = BookStoreServer.not_found_status_code
            self.__books_logger.error(error_message)

        return self.__generate_json_response(result, error_message), status

    def __log_info_delete_book(self, book_title):
        self.__books_logger.info(
            f"Removing book [{book_title}] | request #{self.__current_request_num}")

    def __log_debug_delete_book(self, book_title, book_id, remaining_books):
        self.__books_logger.debug(
            f"After removing book [{book_title}] id: [{book_id}] there are {remaining_books} books in the system | request #{self.__current_request_num}")

    def __generate_json_response(self, result, error_message):
        response_json = self.__json_response_template
        response_json["result"] = result
        response_json["errorMessage"] = error_message
        return response_json

    def __get_logger_level(self):
        logger_name = str(request.args.get("logger-name"))
        if logger_name == "request-logger":
            return self.__get_logger_level_name(self.__request_logger)
        elif logger_name == "books-logger":
            return self.__get_logger_level_name(self.__books_logger)
        else:
            return "invalid logger name, please choose between: request-logger, books-logger."

    # Function to get the current logging level of the logger
    def __get_logger_level_name(self, logger):
        level = logger.getEffectiveLevel()
        return logging.getLevelName(level)

    def __set_logger_level(self):
        logger_name = str(request.args.get("logger-name"))
        logger_level_str = str(request.args.get("logger-level"))

        if logger_level_str in ["ERROR", "INFO", "DEBUG"]:
            new_level = self.__get_logging_level_constant(logger_level_str)
            if logger_name == "request-logger":
                self.__request_logger.setLevel(new_level)
                for handler in self.__books_logger.handlers:
                    handler.setLevel(new_level)
                return logger_level_str
            elif logger_name == "books-logger":
                self.__books_logger.setLevel(new_level)
                for handler in self.__books_logger.handlers:
                    handler.setLevel(new_level)
                return logger_level_str
            else:
                return "invalid logger name, please choose between: request-logger, books-logger."
        return "invalid logger level, please choose between: ERROR, INFO, DEBUG."

    def __get_logging_level_constant(self, level_str):
        return getattr(logging, level_str.upper(), None)


def is_sublist(main_list: list, sub_list: list) -> bool:
    for element in sub_list:
        if element not in main_list:
            return False
    else:
        return True