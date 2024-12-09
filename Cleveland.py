import re
import os
import json
import requests
import sqlite3
import random

# get info for paintings from the API
# input: limit (the number of paintings to pull, auto-set to 25)
# output: paintings (a list of paintings with information from API, each item in list is a painting)
def get_paintings(limit=25):
    # set url
    url = "https://openaccess-api.clevelandart.org/api/artworks"
    
    # set parameters to search for
    # must search for only paintings and only created after 1800
    # set random skip value
    params = {'type': 'Painting', 'created_after': 1800, 'limit': limit, 'skip': random.randint(0, 823-limit)}
    
    # initializes empty list for paintings to return
    paintings = []
    
    # sends request to API, collects data for 25 paintings from API
    # return list of paintings
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()  
        paintings.extend(data['data'])
    else:
        return "Failed to get paintings from API"
    
    return paintings

# set up the database
# input: database_name (a string, the name of the database to open)
# output: cur, conn (a cursor and connection to the database)
def set_up_database(database_name):
    # set path, create conn and cur and return them
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + database_name)
    cur = conn.cursor()
    return cur, conn

# set up the Cleveland table
# inputs: cur, conn (the cursor and connection to the database)
# output: None
def create_Cleveland_table(cur, conn):
    # create table if it doesn't exist
    # includes id_key, title, creation_year, main_artist
    cur.execute("CREATE TABLE IF NOT EXISTS Cleveland (id_key INTEGER PRIMARY KEY, title TEXT UNIQUE, creation_year INTEGER, artist_id INTEGER, department_id INTEGER)")
    return None

# set up the Artist table
# inputs: cur, conn
# output: None
def create_Cleveland_Artist_table(cur, conn):   
    # create table if it doesn't exist
    # includes id, artist
    cur.execute("CREATE TABLE IF NOT EXISTS Cleveland_Artists (id INTEGER PRIMARY KEY, artist TEXT UNIQUE)")
    conn.commit()
    return None
        
# create Departments table
# inputs: cur, conn
# output: None
def create_Cleveland_Departments_table(cur, conn):
    # create table if doesn't exist
    # includes id and department name
    cur.execute("CREATE TABLE IF NOT EXISTS Cleveland_Departments (id INTEGER PRIMARY KEY, department TEXT UNIQUE)")
    conn.commit()
    return None

# insert painting data into the database
def insert_paintings_into_Cleveland(paintings, cur, conn):
    
    # keeps track of paintings inserted into the table to make sure limit is 25
    new_paintings = []
    
    # go through each painting / 25
    for painting in paintings:
        # get the title 
        # if title field empty, insert NULL
        if painting['title']:
            title = re.findall(r'([,\.\w\d\s\'\"-]+)[(]?', painting['title'])[0].strip()
        else:
            title = None
        
        # get the creation_date
        # if empty -> NULL
        if painting['creation_date_latest']:
            creation_date = painting['creation_date_latest']
        else:
            creation_date = None
        
        # get main artist id from Artist table
        # if empty -> NULL
        if painting['creators']:
            cur.execute("SELECT id FROM Cleveland_Artists WHERE artist = ?", (re.findall(r'[\.\w\s-]+', painting['creators'][0]['description'])[0].strip(),))
            result = cur.fetchone()
            if result:
                artist_id = result[0]
            # insert artist name into Artist table if doesn't exist yet
            else:
                cur.execute("INSERT INTO Cleveland_Artists (artist) VALUES (?)", (re.findall(r'[\.\w\s-]+', painting['creators'][0]['description'])[0].strip(),))
                artist_id = cur.lastrowid
        else:
            artist_id = None
        
        # get department id from Department table
        # if empty -> NULL
        if painting['department']:
            cur.execute("SELECT id FROM Cleveland_Departments WHERE department = ?", (painting['department'],))
            result = cur.fetchone()
            if result:
                department_id = result[0]
            # insert Department name into Department table if doesn't exist yet
            else:
                cur.execute("INSERT INTO Cleveland_Departments (department) VALUES (?)", (painting['department'],))
                department_id = cur.lastrowid
        else:
            department_id = None
    
        # insert the data into the Cleveland table
        cur.execute("INSERT OR IGNORE INTO Cleveland (title, creation_year, artist_id, department_id) VALUES (?, ?, ?, ?)", (title, creation_date, artist_id, department_id))

        # if the row was inserted into the table, append painting to the new_painting list
        # print that the painting and artist have been added
        if cur.rowcount > 0:
        # add painting to list to keep track of new paintings added, but only if inserted
            new_paintings.append(painting)
            print(f"added painting title: '{title}' to database")
       
        # if insert was ignored, state reason for ignoring
        # the painting will be ignored if its title is already in the database
        else:
            print(f"painting title: '{title}' already in database")
        
        # stop incrementing if number of newly inserted paintings reaches 25
        # this is an extra precaution in case the limit on the API request is changed to be larger than 25
        if len(new_paintings) == 25:
            break
    
    print(f'added {len(new_paintings)} new paintings to database')
    
    # commit changes and return new_paintings
    conn.commit()
    return new_paintings

def main():
    # make the db, make the table
    cur, conn = set_up_database("Museums.db")
    create_Cleveland_Departments_table(cur, conn)
    create_Cleveland_Artist_table(cur, conn)
    create_Cleveland_table(cur, conn)
    

    # print total number of paintings in db right now
    cur.execute("SELECT COUNT(*) FROM Cleveland")
    paintings_inserted = cur.fetchone()[0]
    print("current painting count: " + str(paintings_inserted))
    
    # call API to get new paintings and insert them into the db
    insert_paintings_into_Cleveland(get_paintings(), cur, conn)
    
    # print total number of paintings in db after calling API
    cur.execute("SELECT COUNT(*) FROM Cleveland")
    paintings_inserted = cur.fetchone()[0]
    print("new painting count: " + str(paintings_inserted))
    conn.close()
    

#run this code multiple times to gather > 100 paintings
main()
