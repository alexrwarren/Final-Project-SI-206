import re
import os
import json
import requests
import sqlite3
import random

# get books information from API
# input: limit (the number of books to gather, auto-set to 100)
# output: books (a list of book information, each entry is a book)
def get_books(limit=100):
    # set url, parameter for subject (fiction) and publishing year range (1800-2024) in url
    url = "https://openlibrary.org/subjects/fiction.json?published_in=1800-2024"
    
    # set search parameters (limit = 100 and offset = random number)
    offset = random.randint(0, 1000)
    params = {'limit': limit, 'offset': offset}
    
    # initializes empty list for books
    books = []
    
    # sends request to API, collects data for 100 books from API
    # return list of books
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()  
        books.extend(data['works'])
    else:
        return None
    
    return books

# set up the database
# input: database_name (name of database to open)
# output: cur, conn (a connection and cursor to the database)
def set_up_database(database_name):
    # set path, create conn and cur and return them
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + database_name)
    cur = conn.cursor()
    return cur, conn

# set up the Open_Library table 
# inputs: cur, conn
# outputs: None
def create_Open_Library_table(cur, conn):
    # create table if it doesn't exist
    # includes id_key, title, creation_year, author_id
    cur.execute("CREATE TABLE IF NOT EXISTS Open_Library (id_key INTEGER PRIMARY KEY, title TEXT UNIQUE, creation_year INTEGER, author_id INTEGER)")
    return None

# set up the Authors table 
# inputs: cur, conn
# outputs: None
def create_Open_Libary_Authors_table(cur, conn):
    # create table if it doesn't exist
    # includes id, author name
    cur.execute("CREATE TABLE IF NOT EXISTS Open_Library_Authors (id INTEGER PRIMARY KEY, author TEXT UNIQUE)")
    conn.commit()
    return None

# insert API data into the database
# input: books (list of books to parse for information -- returned value from get_books)
# inputs: cur, conn
# output: None
def insert_books_into_Open_Library(books, cur, conn):
    
    # keeps track of new books inserted into the table
    new_books = []
    
    # go through each book / 25
    for book in books:
        # get the title 
        # if title field empty, insert NULL
        if book['title']:
            title = book['title'].strip()
        else:
            title = None
        
        # get the first publishing date 
        # if empty -> NULL
        if book['first_publish_year']:
            creation_date = int(book['first_publish_year'])
            if creation_date < 1800:
                continue
        else:
            creation_date = None
        
        # get author name
        # insert it into the author table and fetch author id key
        # if empty -> NULL
        if book['authors']:
            cur.execute("SELECT id FROM Open_Library_Authors WHERE author = ?", (book['authors'][0]['name'],))
            result = cur.fetchone()
            if result:
                author_id = result[0]
            else:
                cur.execute("INSERT INTO Open_Library_Authors (author) VALUES (?)", (book['authors'][0]['name'],))
                author_id = cur.lastrowid
        else:
            author_id = None

        # insert the data into the Open_Library table
        cur.execute("INSERT OR IGNORE INTO Open_Library (title, creation_year, author_id) VALUES (?, ?, ?)", (title, creation_date, author_id))

        # if the row was inserted into the table, append book to the new_book list
        # print that the book has been added
        if cur.rowcount > 0:
        # add book to list to keep track of new books added, but only if inserted
            new_books.append(book)
            print(f"added book title: '{title}' to database")
       
        # if insert was ignored, state reason for ignoring
        # usually the book will be ignored because the title is already in the database
        else:
            print(f"book title: '{title}' already in database")
        
        # stop incrementing if number of newly inserted books reaches 25
        # this is an extra precaution in case the limit on the API request is changed to be larger than 25
        if len(new_books) == 25:
            break
    
    print(f'added {len(new_books)} new books to database')
    
    # commit changes to database
    conn.commit()

def main():
    # make the db, make the table
    cur, conn = set_up_database("Museums.db")
    create_Open_Libary_Authors_table(cur, conn)
    create_Open_Library_table(cur, conn)
    

    # print total number of books in db right now
    cur.execute("SELECT COUNT(*) FROM Open_Library")
    books_inserted = cur.fetchone()[0]
    print("current book count: " + str(books_inserted))
    
    # call API to get new books and insert them into the db
    insert_books_into_Open_Library(get_books(), cur, conn)
    
    # print total number of books in db after calling API
    cur.execute("SELECT COUNT(*) FROM Open_Library")
    books_inserted = cur.fetchone()[0]
    print("new books count: " + str(books_inserted))
    conn.close()
    

#run this code multiple times to gather > 100 books
main()
