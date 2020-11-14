# Project 1

Web Programming with Python and JavaScript

   welcome to my project 1 - a simple responsive book review site with API usage;

   1)  application.py - is the main application that starts with creating table if there isnt one for the users to save user id, username and HASHED-password. after that i define routs for the application. INDEX() is just the first page for people to log in or register. REGISTER() has for the get user input of his username and password(which is hashed) and save into the created user database. LOGIN() lets the users sign in if the input corresponds with the database data. LOGOUT() just clears the session and makes the user return to first page. MAIN() just returns the main page. BOOKS() returns the list of matched books titles and authors. INFO() creates a database for reviews if there isnt any and displays the information about the previousely selected books from the local database and from the goodreads API. on the page the user can submit a review if he/she didnt already submit and also see the other reviews that people left on my web aplication. API() defines the return of the api of information that was left on my web aplication like books-title,author,review count, average rating... 

   2)  import.py - is a python aplication that creates a database for the books and imports books info from books.csv into the table

   3)  helper.py - is an @login_required decorator for users to not acces parts of my web aplication without login.session

   4)  templates - is the folder that holds html files for all the functions previousely defined. layout.html - is the basic layout for all of the files.

   5)  static  - is the folder containing css file which styles html elements. (for my learning porpuses i dont use scss sass to get comfortable with css writing)

  