import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database engine
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def main():
    b=open("books.csv")
    reader=csv.reader(b)
    db.execute("CREATE TABLE books (isbn VARCHAR PRIMARY KEY, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year VARCHAR NOT NULL);")
    db.execute("CREATE TABLE users (user_id SERIAL PRIMARY KEY, username VARCHAR NOT NULL UNIQUE, password VARCHAR NOT NULL);")
    db.execute("CREATE TABLE reviews (review_id SERIAL PRIMARY KEY, isbn VARCHAR REFERENCES books, user_id INTEGER REFERENCES users, review_stars INTEGER NOT NULL, review_details VARCHAR NOT NULL);")

    for isbn, tit, auth, yr in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
        {"isbn":isbn ,"title":tit, "author":auth, "year":yr})
# for better performance i commented the following line
#        print(f"Added book {isbn}, title {tit}, written by {auth}")
    db.commit()
if __name__ =="__main__":
    main()
