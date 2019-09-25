import csv 
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://veufgqrqcdagor:7705973df1ee8412f8adf05f713f3a4c2692d3f79fe7df60101315add082c144@ec2-54-225-95-183.compute-1.amazonaws.com:5432/d6ap38ig08mt8t")
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