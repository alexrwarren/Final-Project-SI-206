import sqlite3
import matplotlib.pyplot as plt
import os
import csv


# get the creation years and heights for paintings from the database
# input: database_name (name of the database to get data from, str)
# output: data (a list of tuples, the creation years and heights in the format (year, height))
def get_years_and_heights(database_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + database_name)
    cur = conn.cursor()

    cur.execute("""
        SELECT creation_year, height_cm FROM Harvard
        WHERE creation_year IS NOT NULL
        AND height_cm IS NOT NULL
    """)
    data = cur.fetchall()
    conn.close()
    #print(f"these are the paintings pulled from the database: {data}")
    return data

# calculate the average heights for paintings within a year interval
# input: data (a list of tuples in the format [(creation year, height in cm), ...])
# input: interval (the interval to determine creation date ranges, default set to 50 years, int)
# output: height_distribution (a dictionary with keys as interval years (e.g. 1900, 1950, 2000) and values as inner dictionaries)
# output: cont. height_distribution (dictionary values = inner dictionary with keys as 'total_height', 'number_of_paintings', and 'average_height' and values as float/ints for the respective key)
# output: interval (same as input, int)
def calculate_average_height(data, interval=50):
        # initializes empty dictionary
    height_distribution = {}

    # for each year, height tuple in painting data...
    for year, height in data:
        #print(f"this is the year of the painting: {year}")
        
        # determine interval year to categorize data based on decade (1924 -> 1920, 1919 -> 1910, etc.)
        interval_key = (year // interval) * interval
        #print(f"this is the interval key of the painting with year = {year}: {interval_key}")
        
        # initialize inner dictionary for each interval key
        if interval_key not in height_distribution:
            height_distribution[interval_key] = {'total_height': 0, 'number_of_paintings': 0, 'average_height': 0}
            #print(f"creating inner dictionary for {interval_key}")
        
        # adds height to the distribution at the interval key
        height_distribution[interval_key]['total_height'] += height
        height_distribution[interval_key]['number_of_paintings'] += 1
        #print(f"this is the current interval information for {interval_key}: {height_distribution[interval_key]}")
    
    # calculates the average height and replaces dictionary value as average
    for interval_key, info in height_distribution.items():
        info['average_height'] = round(info['total_height'] / info['number_of_paintings'], 2)
        #print(f"this is the final interval information for {interval_key}: {height_distribution[interval_key]}")

    return height_distribution, interval

# write the calculations to a csv file
# input: height_data (a dictionary with keys as interval years (e.g. 1900, 1950, 2000) and values as inner dictionaries)
# input: cont. height_data (dictionary values = inner dictionary with keys as 'total_height', 'number_of_paintings', and 'average_height' and values as float/ints for the respective key)
# input: interval (the interval to determine creation date ranges, default set to 50 years, int)
# input: filename (the name of the csv file to write to, string)
# output: None
def write_to_csv_file(height_data, interval, filename):
    with open(filename, 'w') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['Average Height for Paintings in Harvard Art Museums by Date'])
        csv_writer.writerow(['Painting Creation Date Range', 'Average Painting Height (in cm)'])
        for interval_key, info in height_data.items():
            avg_height = info['average_height']
            end_date = interval_key + interval - 1
            years = f"{interval_key}-{end_date}"
            csv_writer.writerow([years, avg_height])
    file.close() 
    
    
# visualize height data as a a bar chart
# input: height_data (a dictionary with keys as interval years (e.g. 1900, 1950, 2000) and values as inner dictionaries)
# input: cont. height_data (dictionary values = inner dictionary with keys as 'total_height', 'number_of_paintings', and 'average_height' and values as float/ints for the respective key)
# input: interval (the interval to determine creation date ranges, default set to 50 years, int)
# output: None
def visualize_height_data(height_data, interval):
    
    # Set lists of data to be charted (intervals, average heights)
    intervals = sorted(height_data.keys())
    heights = [height_data[interval]['average_height'] for interval in intervals]

    # Set interval labels as year range (ex: 1900-1919)
    interval_labels = [f"{interval_start}-{interval_start + interval - 1}" for interval_start in intervals]


    # Create a figure with a bar chart
    plt.figure(figsize=(10, 6))
    
    
    # Plot the bars, make intervals into strings so that the bar will auto-adjust width
    intervals = [str(interval) for interval in intervals]
    plt.bar(intervals, heights, color=['red', 'orange', 'yellow', 'green', 'blue'])

    # Set axis labels and title
    plt.xlabel("Painting Creation Date")
    plt.ylabel("Painting Height (in cm)")
    plt.title("Distribution of Painting Height (in cm) for Artwork at Harvard Art Museums")
    
    # Set x-ticks as interval labels
    plt.xticks(intervals, interval_labels)

    # Save and show the plot
    plt.savefig("Harvard_height_distribution_over_time.png")
    plt.show()
    
def main():
    data = get_years_and_heights("Museums.db")
    height_data, interval = calculate_average_height(data, 50)
    write_to_csv_file(height_data, interval, "Harvard_height_data.csv")
    visualize_height_data(height_data, interval)

main()


