import sqlite3
import matplotlib.pyplot as plt
import os
import csv

# get data from the Cleveland and Cleveland_Departments tables
# input: database_name (name of the database to open)
# output: department_data (a list of every department name for paintings - with duplicates)
def get_data_from_database(database_name):
    
    # establish connection to the database
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + database_name)
    cur = conn.cursor()

    # select department name from Cleveland where the id number matches that in the Cleveland_Department table
    # return list of departments with duplicates 
    cur.execute("""
        SELECT department
        FROM Cleveland_Departments
        JOIN Cleveland
        ON Cleveland.department_id = Cleveland_Departments.id
    """)
    data = cur.fetchall()
    conn.close()
    department_data = [entry[0] for entry in data]
    return department_data

# get frequency count of departments
# input: department_data (list of all departments for paintings in database -- returned from get_data_from_database)
# output: data_dict (dictionary; key = department name, value = frequency count of paintings in department)
def get_frequency_counts(department_data):
    
    # initialize empty dictionary
    # loop through each department in the list, create dictionary entry and increase count value by 1
    data_dict = {}
    for entry in department_data:
        data_dict[entry] = data_dict.get(entry, 0) + 1
    return data_dict

# write counts to a csv file
# input: data_dict (dictionary; keys = department names, values = painting frequency -- returned value from get_frequency_counts)
# input: filename (string; name of file to write department frequency data to)
# output: None
def write_counts_to_file(data_dict, filename):
    
    # if word_dict is empty, exit program
    if not data_dict:
        print("no department frequencies in dictionary")
        exit()
    
    # sort the dictionary items by frequency in descending order
    # turn the list of tuples into a list of lists (for easier conversion in csv file writing)
    sorted_tuples = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)
    sorted_list = [list(tuple) for tuple in sorted_tuples]

    # open a csv file writer
    file = open(filename, 'w')
    csv_writer = csv.writer(file)
    
    # write file header and column names
    csv_writer.writerow([f"Cleveland Museum of Art: Painting Frequency by Department"])
    csv_writer.writerow(['Department', 'Number of Paintings'])
    
    # write a row for each department, frequency pair in list of words
    csv_writer.writerows(sorted_list)
    
    # close the file
    file.close()
    
# visualize the department frequency data as a pie chart
# input: data_dict (dictionary; keys = department names, values = painting frequency -- returned value from get_frequency_counts)
# output: None
def visualize_counts(data_dict):
    # sort the dictionary data by frequency count in descending order
    # set departments as the "keys"
    # set totals as the "values"
    sorted_dict = sorted(data_dict.items(), key=lambda x: x[1])
    departments = [entry[0] for entry in sorted_dict]
    totals = [entry[1] for entry in sorted_dict]
    
    # create the pie chart, add a wedge of 70%
    # create a legend
    # set the title 
    # save the figure
    # show the figure
    plt.figure(1, figsize=(20, 10))  
    plt.pie(totals, labels=departments, autopct='%1.1f%%', pctdistance=0.85, startangle = 90, wedgeprops={'width': 0.7})
    plt.legend(loc="best")
    plt.title("Cleveland Museum of Art: Painting Frequency by Department")  
    plt.savefig("Cleveland_department_frequency.png")  
    plt.show()  
    
    
def main():
    department_data = get_data_from_database("Museums.db")
    data_dict = get_frequency_counts(department_data)
    write_counts_to_file(data_dict, "department_counts.csv")
    visualize_counts(data_dict)

main()