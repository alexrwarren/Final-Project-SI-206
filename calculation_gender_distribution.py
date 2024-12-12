import os
import sqlite3
import matplotlib.pyplot as plt
import csv

# gets data from the database
# input: databse_name (the name of the database, str)
# output: data (a list of creation years and gender ids for each painting in the databse, list of tuples)
def get_data_from_database(database_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + database_name)
    cur = conn.cursor()

    cur.execute("""
        SELECT creation_year, gender_id FROM Met
        WHERE creation_year IS NOT NULL
    """)
    data = cur.fetchall()
    conn.close()
    return data

# processes the data for file writing
# input: data (a list of painting data in format [(painting year, artist gender id), ...])
# input: interval (a year interval to determine the year key from, int (default = 10))
# output: gender_distribution (a dictionary with keys = interval keys (ex: 1900, 1910, 1920, int) and values = dictionary with keys = male/female and values = 0/1 respectively, dict)
def process_data(data, interval=10):
    
    # initializes empty dictionary
    gender_distribution = {}

    # for each year, gender id tuple in painting data...
    for year, gender_id in data:
        
        # determine interval year to categorize data based on decade (1924 -> 1920, 1919 -> 1910, etc.)
        interval_key = (year // interval) * interval
        
        # initialize inner dictionary for each interval key
        if interval_key not in gender_distribution:
            gender_distribution[interval_key] = {'male': 0, 'female': 0}
        
        # adds 1 to count for male/female based on painting artist gender
        if gender_id == 1:
            gender_distribution[interval_key]['female'] += 1
        else:
            gender_distribution[interval_key]['male'] += 1

    return gender_distribution, interval

# writes the gender distribution data to a csv file
# input: gender_distribution (dictionary of dictionaries with gender dist data -- returned from proces_data)
# input: interval (returned from process_data)
# output: None
def write_data_to_csv_file(gender_distribution, interval):
    
    # open file to write to
    with open("Met_gender_distribution_data.csv", "w", newline="") as csvfile:
        
        # make a csv writer
        # write the heading and title
        writer = csv.writer(csvfile)
        writer.writerow(['The Metropolitan Museum of Art: Number of Paintings by Male and Female Artists by Creation Date of Artwork'])
        writer.writerow(["Painting Creation Date", "Number of Paintings by Male Artists", "Number of Paintings by Female Artists"])
        
        interval = interval
        
        for interval_start, counts in sorted(gender_distribution.items()):
            
            # calculate end date for interval
            interval_end = interval_start + (interval - 1)
            interval_range = f"{interval_start}-{interval_end}"
            
            # write counts to file
            male_count = counts['male']
            female_count = counts['female']
            writer.writerow([interval_range, male_count, female_count])

# visualize gender distribution as bar chart
# input: gender_distribution (returned from process_data, dict)
# input: interval (returned from process_data)
# output: png image of bar chart
def plot_gender_distribution(gender_distribution, interval):
    
    # set lists of data to be charted (intervals, male painter counts by interval, female painter counts by interval)
    intervals = sorted(gender_distribution.keys())
    male_counts = [gender_distribution[interval]['male'] for interval in intervals]
    female_counts = [gender_distribution[interval]['female'] for interval in intervals]

    # set interval labels as year range (ex: 1900-1919)
    interval_labels = [f"{interval_start}-{interval_start + interval - 1}" for interval_start in intervals]

    # create a figure with two bar charts, one for female, one for male count
    plt.figure(figsize=(12, 6))
    plt.bar(intervals, male_counts, width=8, label="Paintings by Male Artists", alpha=0.7, color="blue")
    plt.bar(intervals, female_counts, width=8, label="Paintings by Female Artists", alpha=0.7, color="pink", bottom=male_counts)

    # set axis labels and title
    plt.xlabel("Painting Creation Date")
    plt.ylabel("Number of Paintings")
    plt.title("The Metropolitan Museum of Art: Number of Paintings by Male and Female Artists by Creation Date of Artwork")
    
    # create a legend
    plt.legend()
    
    # set x ticks as interval labels
    plt.xticks(intervals, interval_labels)  
    plt.tight_layout()

    plt.savefig("Met_gender_distribution_over_time.png")
    plt.show()

def main():
    database_name = "Museums.db"
    data = get_data_from_database(database_name)
    gender_distribution, interval = process_data(data, 20)
    
    write_data_to_csv_file(gender_distribution, interval)
    
    plot_gender_distribution(gender_distribution, interval)

if __name__ == "__main__":
    main()
