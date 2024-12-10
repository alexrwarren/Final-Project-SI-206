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
        WHERE creation_year IS NOT NULL
        AND height_cm IS NOT NULL
    """)
    data = cur.fetchall()
    conn.close()
    return data

def calculate_average_height(data):
    height_dist = {}

    early_eighteen_count = 0
    late_eighteen_count = 0
    early_nineteen_count = 0
    late_nineteen_count = 0
    early_2000s_count = 0
    
    for creation_year, height_cm in data:
        if 1800 <= creation_year <= 1851:
            if '1800-1850' not in height_dist:
                height_dist['1800-1850']  = 0
            height_dist['1800-1850'] += height_cm
            early_eighteen_count += 1

        elif 1851 <= creation_year <= 1900:
            if '1851-1900' not in height_dist:
                height_dist['1851-1900']  = 0
            height_dist['1851-1900'] += height_cm
            late_eighteen_count += 1

        elif 1901 <= creation_year <= 1950:
            if '1901-1950' not in height_dist:
                height_dist['1901-1950']  = 0
            height_dist['1901-1950'] += height_cm
            early_nineteen_count += 1

        elif 1951 <= creation_year <= 2000:
            if '1951-2000' not in height_dist:
                height_dist['1951-2000']  = 0
            height_dist['1951-2000'] += height_cm
            late_nineteen_count += 1

        elif 1951 <= creation_year <= 2000:
            if '2000-2050' not in height_dist:
                height_dist['2000-2050']  = 0
            height_dist['2000-2050'] += height_cm
            early_2000s_count += 1

        count_lst = [early_eighteen_count, late_eighteen_count, early_nineteen_count, late_nineteen_count, early_2000s_count]

    index = 0
    for key in height_dist:
        average = round((height_dist[key]) / (count_lst[index]), 2)
        height_dist[key] = average
        index += 1

    return height_dist

def plot_average_height(dist):

    plt.figure(figsize= 10)

    time_periods = list(dist.keys())
    averages = list(dist.values())

    plt.bar(time_periods, averages, color = ['red', 'orange', 'yellow', 'green', 'blue'])

    plt.xlabel('Time Periods')
    plt.ylabel('Painting Height in cm')
    plt.title('Average Painting Height Each Half-Century Since 1800')
    plt.legend()
    plt.ticklabel_format(rotation = 45)

    plt.savefig('average_painting_height_in_cm.png')
    plt.show()


def write_csv_file(filename, dist):
    with open(filename, "w") as file:
        file.write("Average Painting Height Each Half-Century Since 1800:\n")
        for time_period, average in dist.items():
            file.write(f"Average height for Harvard Art Museums' paintings made between {time_period}: {average} cm.\n")

def main():
    database = "Museums.db"
    data = get_data(database)

    # calculate data
    height_distribution = calculate_average_height(data)

    # write txt file
    write_csv_file('average_painting_height_in_cm', height_distribution)

    # plot data
    plot_average_height(height_distribution)

if __name__ == "__main__":
    main()