import sqlite3
import matplotlib.pyplot as plt
import os
import csv

# get data from Cleveland and Departments tables
# input: database_name (string; name of database containing the Cleveland tables)
# output: titles_and_departments (list; tuples containing title and department for each painting in Cleveland table)
def get_data_from_database(database_name):
    
    # establish connection to database
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + database_name)
    cur = conn.cursor()

    # select the painting title and department name for each painting
    # return data as a list of tuples
    cur.execute("""
        SELECT Cleveland.title, Cleveland_Departments.department
        FROM Cleveland
        JOIN Cleveland_Departments
        ON Cleveland.department_id = Cleveland_Departments.id
    """)
    titles_and_departments = cur.fetchall()
    conn.close()
    return titles_and_departments

# get painting title length averages based on department
# input: titles_and_departments (a list of tuples in the format (painting title, department) -- retuened from get_data_from_database)
# output: averages_dict (a dictionary of painting title length averages by department; key = dept string, value = average length float)
def get_painting_title_length_averages(titles_and_departments):
    
    # initialize empty dictionary for averages
    averages_dict = {}
    
    # loop through each title and department in list
    # create a key in the dict using the department name
    # the value of the key is a list of every title length (format = [int, int, int, ...])
    for title, department in titles_and_departments:
        if department not in averages_dict:
            averages_dict[department] = []
        title_length = len(title.strip().split()) 
        averages_dict[department].append(title_length)
        
    # calculate the average of every title length list in the dictionary
    # return the averages dictionary
    for department, lst in averages_dict.items():
        average = round(sum(lst) / len(lst), 2)
        averages_dict[department] = average
    return averages_dict

# write title length averages to a csv file
# input: averages_dict (dictionary; key = department string, value = average painting title length in words float; -- retured from get_painting_title_length_averages)
# input: filename (string; the name of the csv file to write to)
# output: none
def write_calculations_to_csv(averages_dict, filename):
    
     # if word_dict is empty, exit program
    if not averages_dict:
        print("no department title length averages in dictionary")
        exit()
    
    # sort the dictionary items by title length average in descending order
    # turn the list of tuples into a list of lists (for easier conversion in csv file writing)
    sorted_tuples = sorted(averages_dict.items(), key=lambda x: x[1], reverse=True)
    sorted_list = [list(tuple) for tuple in sorted_tuples]

    # open a csv file writer
    file = open(filename, 'w')
    csv_writer = csv.writer(file)
    
    # write file header and column names
    csv_writer.writerow([f"Cleveland Museum of Art: Painting Title Length Average by Department"])
    csv_writer.writerow(['Department', 'Title Length Average (in Words)'])
    
    # write a row for each department, average pair in list of words
    csv_writer.writerows(sorted_list)
    
    # close the file
    file.close()

# visualize the department averages in a bar chart
# input: averages_dict (dictionary; key = department string, value = average painting title length in words float; -- retured from get_painting_title_length_averages)
# output: bar graph as png image
def visualize_averages_by_department(averages_dict):
    # sort dictionary by values (averages) in descending order
    # set departments (all keys) and averages (all values) as seperate lists
    # set a colors list with more colors than necessary
    sorted_dict = sorted(averages_dict.items(), key=lambda x: x[1], reverse = True)
    departments = [entry[0] for entry in sorted_dict]
    averages = [entry[1] for entry in sorted_dict]
    colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'black', 'brown']
    
    # create bar graph
    # set labels
    # set title
    plt.figure(figsize=(16, 8))
    plt.bar(departments, averages, edgecolor = 'black', color=colors)
    plt.xlabel('Department')
    plt.ylabel('Average Painting Title Length (in Words)')
    plt.title("Cleveland Museum of Art: Painting Title Length Average by Department")
    
    # rotate the x axis labels so that they're not cut off/overlapping
    plt.xticks(rotation=45, ha="right")
   
    # save figure as a png image
    # show the figure
    plt.tight_layout()
    plt.savefig("Cleveland_length_by_dept.png")
    plt.show()
    
def main():
    titles_and_departments = get_data_from_database("Museums.db")
    averages_dict = get_painting_title_length_averages(titles_and_departments)
    write_calculations_to_csv(averages_dict, 'Cleveland_length_by_department.csv')
    visualize_averages_by_department(averages_dict)

main()