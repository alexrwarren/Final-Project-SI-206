import sqlite3              
import matplotlib.pyplot as plt     
import os                           
import csv                          


# function: connect to a database and pull necessary variables (creation year, height) for analysis
# input: database (name of the database to connect to, str)
# output: data (list, a list of tuples in the format (creation year, height) for each painting pulled from the database)
def get_data(database):
    path = os.path.dirname(os.path.abspath(__file__))           # establish path to database
    conn = sqlite3.connect(path + "/" + database)               # establish connection
    cur = conn.cursor()                                         # create cursor

    # gather creation_year and height_cm variables from Harvard table in Museums.db database
    cur.execute("""                                             
        SELECT creation_year, height_cm FROM Harvard
        WHERE creation_year IS NOT NULL
        AND height_cm IS NOT NULL
    """)
    data = cur.fetchall()
    conn.close()
    return data


# function: create dictionary with time periods of painting's creation as the keys and a list of painting heights in that time period as the values
# input: data (a list of tuples, returned from get_data())
# output: height_dist (dict, a dictionary containing the time periods as keys (type = str) painting height averages as values (type = float))
def calculate_average_height(data):
    height_dist = {}                                # create empty dictionary                      
    
    for creation_year, height_cm in data:           # filter painting data based on creation_year variable and sum total painting heights
        if 1800 <= creation_year < 1850:
            if '1800-1849' not in height_dist:
                height_dist['1800-1849']  = {"heights": []}    # if first collected painting for a time period, create an integer placeholder
            height_dist['1800-1849']['heights'].append(height_cm)  # add painting height onto the current list for painting heights in that time period

        elif 1850 <= creation_year < 1900:
            if '1850-1899' not in height_dist:
                height_dist['1850-1899']  = {"heights": []}
            height_dist['1850-1899']['heights'].append(height_cm)

        elif 1900 <= creation_year < 1950:
            if '1900-1949' not in height_dist:
                height_dist['1900-1949']  = {"heights": []}
            height_dist['1900-1949']['heights'].append(height_cm)

        elif 1950 <= creation_year < 2000:
            if '1950-1999' not in height_dist:
                height_dist['1950-1999']  = {"heights": []}
            height_dist['1950-1999']['heights'].append(height_cm)

        elif 2000 <= creation_year <= 2050:
            if '2000-2049' not in height_dist:
                height_dist['2000-2049']  = {"heights": []}
            height_dist['2000-2049']['heights'].append(height_cm)
    
    for key, heights in height_dist.items(): # iterates through each time period and height list in the dictionary
        average_height = round(sum(heights['heights']) / len(heights['heights']), 2) # calculates the average painting height from the list
        height_dist[key] = average_height # replaces the dictionary value at the year range key with the average painting height

    return height_dist

# writes the height averages to a csv file
# input: filename (str, the name of the file to write to)
# input: dist (dict, a dictionary containing the time periods as keys (type = str) painting height averages as values (type = float))
# output: None
def write_heights_to_csv_file(filename, dist):
    with open(filename, "w") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["Harvard Art Museums: Average Painting Height (cm) by Date of Creation"])
        csv_writer.writerow(['Painting Creation Date', 'Average Painting Height (in cm)'])

        sorted_tups = sorted(list(dist.items()), key = lambda x: x[0])

        for time_period, average in sorted_tups:
            csv_writer.writerow([time_period, average])
    file.close()
    
# function: create a bar chart for the average painting heights
# input: height_dist (a dictionary of the time periods and heights for the paintings in the Harvard table, dict, keys = time periods (str), values = height averages (float))
# output: None
def plot_average_height(height_dist):

    plt.figure(figsize= (10,6)) # set the figure size

    sorted_tups = sorted(list(height_dist.items()), key = lambda x: x[0]) # sort the dictionary by year range (1800 first, 2000 last)

    time_periods = [x[0] for x in sorted_tups] # makes a list of time periods from dataset
    averages = [x[1] for x in sorted_tups] # makes a list of painting height averages from dataset
 
    plt.bar(time_periods, averages, edgecolor = 'black', color = ['red', 'orange', 'yellow', 'green', 'blue'])

    # set labels + title
    plt.xlabel('Painting Creation Date')
    plt.ylabel('Painting Height (cm)')
    plt.title("Harvard Art Museums: Average Painting Height (cm) by Date of Creation")
    plt.tight_layout()
    plt.savefig('Harvard_average_painting_height_in_cm.png')
    plt.show()

def main():
    database = "Museums.db"
    data = get_data(database)

    # calculate data
    height_distribution = calculate_average_height(data)

    # write csv file
    write_heights_to_csv_file('Harvard_average_painting_height_in_cm.csv', height_distribution)

    # plot data
    plot_average_height(height_distribution)

if __name__ == "__main__":
    main()