import re
import os
import json
import requests
import sqlite3
import random

# gets paintings from API
# input: limit (the maxiumum number of paintings' info to return, int)
# output: object_ids (a list of object ids pulled from the API, each object id represents a Met painting, list)
def get_paintings(limit=100):
    
    # set url for API with correct endpoint
    url = "https://collectionapi.metmuseum.org/public/collection/v1/search"
    
    # Set parameters to search for paintings only
    params = {
        'medium': 'Paintings', 
        'q': '*'
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        total_paintings = data['total']
        object_ids = data['objectIDs']
        
        # gather a random sample of the object ids with len = limit
        if total_paintings > limit:
            return random.sample(object_ids, limit)
        else:
            return object_ids[:limit]
    else:
        return None
    

# sets up the database
# input: database_name (the name of the database to create; str)
# output: cur, conn (a cursor and connection to the database)
def set_up_database(database_name):
    # set path, create conn and cur and return them
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + database_name)
    cur = conn.cursor()
    return cur, conn

# sets up the MET table with columns for id key, title, creation year, and gender id
# input: cur, conn (the cursor and connection to the database)
# output: None
def create_MET_table(cur, conn):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Met (
        id_key INTEGER PRIMARY KEY,
        title TEXT UNIQUE,
        creation_year INTEGER,
        gender_id INTEGER
    )
    """)
    conn.commit()


# insert painting data into the database
# input: paintings (a list of object ids -- returned from get_paintings, list)
# inputs: cur, conn
# output: new_paintings (a list of object ids that were added to the database during the function call, list)
def insert_paintings_into_MET(paintings, cur, conn):
    new_paintings = []
    
    for painting_id in paintings:
        # fetch individual painting data
        url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{painting_id}"
        response = requests.get(url)
        
        if response.status_code == 200:
            painting = response.json()

            acceptable_classifications = ['Paintings', 'Paintings-Decorative', 'Bark-Paintings']

             # if artwork isn't a painting, try next object id
            if painting.get('classification') not in acceptable_classifications:
                continue
            
            # if artwork was made before 1800 or doesn't have an end date, try next object id
            if painting['objectEndDate'] < 1800 or not painting['objectEndDate'] or painting['objectEndDate'] > 2024:
                continue
            
            # Extract title from painting data
            if painting['title']:
                title = re.findall(r"[^(]+", painting['title'])[0].strip()
                #print(title)
            else:
                title = None
            
            # Extract creation year from painting data
            creation_year = painting['objectEndDate']
            
            # Extract artist gender from painting data (None = male in API data) 
            # Set gender to 1 if female, 0 if male
            if painting["artistGender"]:
                gender_id = 1
                #print(gender_id)
            else:
                gender_id = 0
            
            # Insert data into the MET table
            cur.execute("INSERT OR IGNORE INTO Met (title, creation_year, gender_id) VALUES (?, ?, ?)", 
                        (title, creation_year, gender_id))
            
            if cur.rowcount > 0:
                new_paintings.append(painting_id)
                print(f"Added painting: '{title}' to database")
            else:
                print(f"Painting: '{title}' already in database")
            
            # if 25 paintings added, stop adding more
            if len(new_paintings) == 25:
                break
    
    print(f'Added {len(new_paintings)} new paintings to database')
    conn.commit()
    
    return new_paintings

def main():
    cur, conn = set_up_database("Museums.db")
    create_MET_table(cur, conn)


    # print total number of paintings in db right now
    cur.execute("SELECT COUNT(*) FROM Met")
    paintings_inserted = cur.fetchone()[0]
    print("current painting count: " + str(paintings_inserted))
    
    # call API to get new paintings and insert them into the db
    insert_paintings_into_MET(get_paintings(), cur, conn)
    
    # print total number of paintings in db after calling API
    cur.execute("SELECT COUNT(*) FROM Met")
    paintings_inserted = cur.fetchone()[0]
    print("new painting count: " + str(paintings_inserted))
    conn.close()
    
# run code multiple times to collect > 100 paintings
main()

