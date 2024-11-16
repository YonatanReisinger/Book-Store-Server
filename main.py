from BookStoreServer import BookStoreServer
from BooksStore import BookStore
import sys
import logging
import click

# Patch the click.echo function
def patched_echo(message=None, file=None, nl=True, err=False, color=None):
    if file is None:
        file = sys.stdout  # Default to stdout if file is None
    click.utils._default_text_stdout().write(message + ('\n' if nl else ''))

click.echo = patched_echo

# Ensure standard output and error are properly set up for Windows
if sys.stdout is None:
    sys.stdout = open('NUL', 'w')
if sys.stderr is None:
    sys.stderr = open('NUL', 'w')

# Set up logging to ensure any print statements or logs are visible
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    genres_lst = ["SCI_FI", "NOVEL", "HISTORY", "MANGA", "ROMANCE","PROFESSIONAL"]
    range_of_valid_publication_year = (1940, 2100)
    books_properties = ["id", "title", "author", "price", "year", "genres"]

    book_store = BookStore(genres_lst, range_of_valid_publication_year, books_properties)

    server = BookStoreServer(host="0.0.0.0", port=8574, book_store=book_store)
    server.run()




