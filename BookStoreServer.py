from flask import Flask, request

class BookStoreServer:

    def __init__(self, host: str, port: int):
        self.__app = Flask(__name__)
        self.__host = host
        self.__port = port
        self.setup_routes()

    def setup_routes(self):
        self.__app.add_url_rule("/", "index", self.index)
        self.__app.add_url_rule("/greet", "greet", self.greet, methods=["GET"])


    def index(self):
        return "Hello World"

    def greet(self):
        name = request.args.get('name', 'World')
        return f"Hello, {name}!"

    def run(self):
        self.__app.run(self.__host, self.__port)