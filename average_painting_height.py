import sqlite3
import matplotlib.pyplot as plt
import os
import numpy as np

def get_data(database):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + database)
    cur = conn.cursor()

    cur.execute("""
        SELECT creation_year, height_cm FROM Harvard
        WHERE height_cm IS NOT NULL
    """)
    data = cur.fetchall()
    conn.close()
    return data

def calculate_average_height(data):
    height_dist = {'1800-1850': 0, '1851-1900': 0, '1901-1950': 0, '1951-2000': 0, '2000-2050': 0}

    for creation_year, height_cm in data:
        if 1800 <= creation_year <= 1851:
            height_dist['1800-1850'] += height_cm
        elif 1851 <= creation_year <= 1900:
            height_dist['1851-1900'] += height_cm
        elif 1901 <= creation_year <= 1950:
            height_dist['1901-1950'] += height_cm
        elif 1951 <= creation_year <= 2000:
            height_dist['1951-2000'] += height_cm
        else:
            height_dist['2000-2050'] += height_cm

    for key in height_dist:
        height_dist[key] = np.mean(height_dist[key])

    return height_dist

def plot_average_height(dist):
    early_eighteen = dist[0]
    late_eighteen = dist[1]
    early_nineteen = dist[2]
    late_nineteen = dist[3]
    early_2000s = dist[4]

    plt.figure(figsize= 10)
    plt.bar(early_eighteen, label = "1800-1850s", color = 'red')
    plt.bar(late_eighteen, label = "1851-1900s", color = 'orange')
    plt.bar(early_nineteen, label = "1901-1950s", color = 'yellow')
    plt.bar(late_nineteen, label = "1951-2000s", color = 'green')
    plt.bar(early_2000s, label = "2000-2050s", color = 'blue')

    plt.xlabel('Time Periods')
    plt.ylabel('Painting Height in cm')
    plt.title('Average Painting Height Each Half-Century Since 1800')
    plt.legend()
    plt.ticklabel_format(rotation = 45)

    plt.savefig('average_painting_height_in_cm.png')
    plt.show()

    

def write_txt_file(dist):

    pass

def main():
    database = "Museums.db"
    data = get_data(database)

    # calculate data
    height_distribution = calculate_average_height(data)

    # write txt file
    write_txt_file(height_distribution)

    # plot data
    plot_average_height(height_distribution)

if __name__ == "__main__":
    main()