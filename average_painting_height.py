import sqlite3
import matplotlib.pyplot as plt
import os

def get_data(database):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + database)
    cur = conn.cursor()

    cur.execute("""
        SELECT height_cm FROM Harvard
        WHERE height IS NOT NULL
    """)
    data = cur.fetchall()
    conn.close()
    return data