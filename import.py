import csv 
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://cizlmooelkynwb:2423acbbe51bf4908f28f10c6edc3adddbf2f7cf8aae2be53be57edd0684b010@ec2-174-129-27-158.compute-1.amazonaws.com:5432/dfo8gj0a4g5mo0")
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
            {"isbn": isbn, "title": title, "author": author, "year": year})
    db.commit()
if __name__ == "__main__":
    main()        