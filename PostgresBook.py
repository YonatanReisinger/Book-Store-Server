from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

class PostgresBook(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    year = Column(Integer)
    price = Column(Integer)
    genres = Column(String)  # Storing genres as a comma-separated string

    def __init__(self, id, title, author, year, price, genres):
        self.id = id
        self.title = title
        self.author = author
        self.year = year
        self.price = price
        # Join list of genres into a single string if provided as list
        self.genres = ','.join(genres) if isinstance(genres, list) else genres

    def get_genres(self):
        # Return genres as a list by splitting the stored string
        return self.genres.split(',') if self.genres else []