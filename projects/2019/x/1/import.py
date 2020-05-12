#!/usr/bin/env python

import os

import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


def main():
    """Read the books.csv file and update the book table on the database"""

    # Check for database environment variable
    if not os.getenv("DATABASE_URL"):
        raise RuntimeError("DATABASE_URL is not set")

    # Set up database
    engine = create_engine(os.getenv("DATABASE_URL"))
    db = scoped_session(sessionmaker(bind=engine))

    # Read file and update table on database
    with open("./books.csv") as file:
        books = csv.reader(file)
        for isbn, title, author, year in books:
            try:
                db.execute(
                    "INSERT INTO books (isbn, title, author, year) \
                    VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": int(year)})
            except ValueError:
                pass

        db.commit()


if __name__ == "__main__":
    main()
