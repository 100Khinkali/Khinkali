import os, csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

db.execute("CREATE TABLE IF NOT EXISTS books(isbn varchar(20) NOT NULL, title varchar(255) NOT NULL, author varchar(255) NOT NULL, year varchar(10) NOT NULL)")
db.commit()

f = open("books.csv")

read = csv.reader(f)

for isbn, title, author, year in read:
	db.execute("INSERT INTO books(isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
					{ "isbn":isbn,
					  "title":title,
					  "author":author,
					  "year":year})
	
	db.commit()
