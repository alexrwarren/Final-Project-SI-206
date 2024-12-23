# import python libraries as needed

import re
import os
import json
import requests
import sqlite3
import random

# gets paintings from API
# input: none
# output: list of paintings from Harvard Art Museums
def get_paintings():
    
    # Harvard Art Museums API stores painting entries in pages, this variable "page" chooses one to then use as a parameter in the url
    page = random.randint(0,100)

    # set url with API key
    key = 'c3ba3791-48c2-42a6-b592-6b8b7b26aebd'
    url =  f"https://api.harvardartmuseums.org/object?apikey={key}"

    # set parameters to pull only 25 paintings at a time from the chosen page
    params = {'size': 25, 'classification': 'Paintings', 'page': page}

    # initializes empty list of paintings to return
    paintings = []

    # sends request to API
    response = requests.get(url, params=params)

    if response.status_code == 200:
        print("yes")
        data = response.json()
        paintings.extend(data['records'])     # adds new paintings to list of paintings
    else:
        return 'Fail'
    
    return paintings

# set up the database
# input: database_name (a string, the name of the database to open)
# output: cur, conn (a cursor and connection to the database)
def create_database(databasename):
    path = os.path.dirname(os.path.abspath(__file__))           # establish path to database
    conn = sqlite3.connect(path + '/' + databasename)           # establish connection
    cur = conn.cursor()                                         # create cursor
    return cur, conn


# set up the Harvard table
# inputs: cur, conn (the cursor and connection to the database)
# output: None
def create_harvard_table(cur, conn):

    # create table if it doesn't exist
    # includes id_key, title, creation_year, height_cm
    cur.execute('''
                CREATE TABLE IF NOT EXISTS Harvard 
                (id_key INTEGER PRIMARY KEY, 
                title TEXT UNIQUE, 
                creation_year INTEGER,
                height_cm FLOAT)
                ''')
    return None

# insert painting data into the database
# inputs: list of painting entries from the API, cursor, connection to the database
# output: list of new paintings added to the database
def insert_paintings_into_harvard(paintings, cur, conn):
    
    # keeps track of paintings inserted into the table
    new_paintings = []
    
    # iterates through each painting entry in the list from the API
    for painting in paintings:

        # locate title
        if painting['title']:
            title = re.findall(r"[^(]+", painting['title'])[0].strip()     # use regex to find title
        else:
            title = None

        # locate date the painting was created
        if painting['dateend']:
            if painting['dateend'] >= 1800:     # only gather paintings created after 1800
                creation_year = painting['dateend'] 
            else:
                continue
        else:
            continue
        
        # locate height of the painting
        if painting['dimensions']:
            height_cm = re.findall(r'\d+[.]?\d+', painting['dimensions'])[0]    # use regex to find height
            height_cm = float(height_cm)
        else:
            height_cm = None

        # insert title, creation_year, and height_cm of each painting into Harvard table in Museums.db database   
        cur.execute('''
                        INSERT OR IGNORE INTO Harvard
                        (title, creation_year, height_cm)
                        VALUES (?,?,?)
                        ''',
                        (title, creation_year, height_cm)
                        )
        
        # add paintings new to the database also into new_paintings list
        if cur.rowcount > 0:
            new_paintings.append(painting)
            print(f"added painting title: '{title}' to database")       # print confirmation of success
        else:
            print(f"painting '{title}' is already in database")         # print notice saying this painting is already in the database

        # ensure only 25 are added to the database at a time
        if len(new_paintings) == 25:
            break

    # print confirmation of how many new paintings were added into the database out of the 25 pulled each run    
    print(f"Added {len(new_paintings)} new paintings to database")

    # commit changes
    conn.commit()

    # return list of new paintings out of the 25 pulled
    return new_paintings

def main():

    # make the database, make the table
    cur, conn = create_database("Museums.db")
    create_harvard_table(cur, conn)

    # print current number of paintings in database
    cur.execute("SELECT COUNT(*) FROM Harvard")
    paintings_inserted = cur.fetchone()[0]
    print("current painting count: " + str(paintings_inserted))
    
    # call API to get new paintings and insert them into the database
    insert_paintings_into_harvard(get_paintings(), cur, conn)
    
    # print total number of paintings in database after calling API
    cur.execute("SELECT COUNT(*) FROM Harvard")
    paintings_inserted = cur.fetchone()[0]
    print("new painting count: " + str(paintings_inserted))
    conn.close()

main()