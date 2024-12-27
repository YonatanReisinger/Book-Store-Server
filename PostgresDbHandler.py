from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()

class PostgresDbHandler:
    def __init__(self, db_url, echo_flag=False):
        """
        Initializes the database handler with a connection to the PostgreSQL database.
        Args:
            db_url (str): Database connection URL in the format:
                          postgresql://username:password@host:port/dbname
            echo_flag (bool): If set to True, SQL statements will be logged.
        """
        self.engine = create_engine(db_url, echo=echo_flag)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)

    def create_tables(self):
        """
        Creates all tables in the database based on the metadata.
        """
        Base.metadata.create_all(self.engine)

    def get_session(self):
        """
        Provides a thread-safe session for database operations.
        Returns:
            Session: A new session object.
        """
        return self.Session()

    def close_session(self, session=None):
        """
        Closes the session.
        Args:
            session (Session, optional): The session to close. Defaults to None.
        """
        if session:
            session.close()

    def dispose_engine(self):
        """
        Disposes of the connection pool used by the engine.
        """
        self.engine.dispose()

    def commit_session(self, session):
        """
        Commits the current transaction.
        Args:
            session (Session): A session object to commit.
        """
        try:
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e

    def __enter__(self):
        """
        Enables the use of the 'with' statement to manage sessions.
        Returns:
            PostgresDbHandler: Self
        """
        self.session = self.get_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Ensures the session is closed when exiting the 'with' block.
        """
        self.commit_session(self.session)
        self.close_session(self.session)
        if exc_val:
            raise exc_val

# Example usage:
db_handler = PostgresDbHandler('postgresql://user:password@localhost:5432/mydatabase')
with db_handler as handler:
    session = handler.session
    # Perform database operations
    # Session is automatically committed and closed
