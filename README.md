# Project 1

## Web Programming with Python and JavaScript
This Project is part of Harvard CS50W course provided by edx portal

## Browse the deployed application in Heroku
### <https://bookshelf-eg.herokuapp.com>

## Description
This project contains:
* __Registration form:__ for signing up and become a member in order to search, review and rate books.
* __Login form:__ using username and password ( password hash saved in database instead of saving the password in plain text) using passlib library.
* __Logout:__ to clear session.
* __Search box:__ is not shown in the homepage or any page in the website until the user logged in.
  user can search by ISBN number , title or author even if the query in the middle of text.
* __Results page:__ the count of results is displayed and the results of search.
* __Homepage:__ in every refresh of the homepage, 10 random box are displayed and user will not able to view book page until he login in. (using shuffle from Random and limit in jinja2 the first 10 records.
* __Last rated books:__ last rated books are shown here.
* __Book page:__ for every book in website, a page is created displaying book title, author, publication year, and ISBN number and all reviews left by users and their ratings in addition of reviews count.
* ~~__Goodreads reviews:__ the average rating and number of ratings for the book also ISBN13 are displayed as received from  Goodreads using their API.~~
> As of December 8th 2020, Goodreads is no longer issuing new developer keys for our public developer API and plans to retire these tools. and I got an email saying that my developer API key has been deactivated due to 30 days of inactivity, So I just used Google books API.
* __Google Books reviews:__ the average rating, number of ratings for the book, ISBN13 are displayed, also added a Preview Link for the book from Google Books.
* __Book cover photo:__ I used Google books API for fetching book cover for books ~~as Goodreads is not providing this option~~ and display book cover in the Book page.
* __Review submission:__ on the book page, user is able to submit only 1 review per book and rate the book on scale of 1 to 5, 1 for lowest and 5 for the highest rating and to write his opinion about the book.
* __API access:__ users can access my website books data using my own API provided the ISBN number, by accessing website ```/api/<isbn>```

## Utilities I have used
* __Cygwin:__ I used [cygwin](https://cygwin.com/) to run psql command on Windows, very handy utility to run Postgres sql database queries.
* __Atom:__ [Text editor](https://atom.io/) I Love.
* __PIP Freeze:__ for auto generating requirements.txt ```$ pip freeze > requirements.txt```

## This Project by
[Magdi Nakhla](https://fb.me/nakhla)
