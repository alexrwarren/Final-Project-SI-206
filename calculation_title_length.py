import os
import sqlite3
import matplotlib.pyplot as plt
import csv

# opens the data base
# input: database name
# output: cur, conn (connection and cursor for the database)
def open_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + db_name)
    cur = conn.cursor()
    return cur, conn

# calculates the average title length for data based on API / source
# input: table_names (list of table names; table names should include all tables that contain painting/book title info)
# output: source_averages_dict (dictionary; keys= source, values = artwork title length average)
def calculate_title_length_averages_by_source(cur, conn, table_names):
    source_averages_dict = {}
    
    # error handling if table doesn't exist in db
    for table in table_names:  
        try:
            cur.execute(f"SELECT title FROM {table}")
        except:
            return "table not in database"
        titles = cur.fetchall()
        
        # calculate title length for each painting/book in words
        object_title_lengths = [len(title[0].split()) for title in titles]
        
        # calculate overall average title length for each source
        average_object_title_length = round(sum(object_title_lengths) / len(object_title_lengths), 2)
        
        # sets the medium as "books" for open_library, as "paintings" for all other sources
        # inserts the average title length for each source to the dictionary
        if table == 'Open_Library':
            if table not in source_averages_dict:
                source_averages_dict[table] = {}
            source_averages_dict[table]['medium'] = 'book'
            source_averages_dict[table]['average title length'] = average_object_title_length
        elif table == 'Harvard' or table == 'Met' or table == 'Cleveland':
            if table not in source_averages_dict:
                source_averages_dict[table] = {}
            source_averages_dict[table]['medium'] = 'painting'
            source_averages_dict[table]['average title length'] = average_object_title_length
        
        # extra pre-caution to skip tables that aren't in db
        else:
            continue
    return source_averages_dict

# writes title lengths to a csv file
# input: source_averages_dict (dictionary; keys= source, values = artwork title length average)
# input: filename (string, name of file to write to)
# output: none
def write_lengths_to_csv_file(source_averages_dict, filename):
    
    # opens file in write mode, makes a csv_writer object
    # write heading and column names
    # write row for each source
    with open(filename, "w") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['Average Artwork Title Length (in Words) by Source/API'])
        csv_writer.writerow(['Source/API', 'Art Medium', 'Average Artwork Title Length (in Words)'])
        for source, values in source_averages_dict.items():
            medium = values['medium']
            average = values['average title length']
            csv_writer.writerow([source, medium, average])
    file.close()

# makes a bar graph visualization of title length averages by source
# input: source_averages_dict (dictionary; keys= source, values = artwork title length average)
# output: png image of figure
def visualize_title_lengths(source_averages_dict):
    sources = list(source_averages_dict.keys())
    source_values = list(source_averages_dict.values())
    source_averages = [value['average title length'] for value in source_values]
    
    # make the figure and bar graph
    # set x, y labels and title
    plt.figure(1, figsize=(20, 10))
    plt.bar(sources, source_averages, color=['blue', 'red', 'purple', 'pink'])
    plt.xlabel("Source/API")
    plt.ylabel("Average Artwork Title Length (in Words)")
    plt.title("Average Artwork Title Length (in Words) by Source/API")
    
    # save figure as png and show it
    plt.savefig("title_word_lengths_by_medium.png")
    plt.show()
    
    
def main():
    table_names = ['Cleveland']
    cur, conn = open_database("Museums.db")
    source_averages_dict = calculate_title_length_averages_by_source(cur, conn, table_names)
    write_lengths_to_csv_file(source_averages_dict, "title_lengths.csv")
    visualize_title_lengths(source_averages_dict)

main()
