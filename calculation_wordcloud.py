import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import sqlite3
import matplotlib.pyplot as plt
import os
import csv
import re

# get words from database
# input: table_names (list of table names to get title words for)
# input: database_name (the name of the database to open)
# output: words (a list of all of the words from artwork titles -- no separation between tables, duplicate words present)
def get_words_from_database(table_names_lst, database_name):
    # establish connection and cursor to the database
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + database_name)
    cur = conn.cursor()
    
    # initialize an empty list of words to be returned
    words = []
    
    # iterate through each table in the list of names
    # try to select every title from the table (exit function if title column or table name not found)
    for table in table_names_lst:
        try:
            cur.execute(f"SELECT title FROM {table}")
        except:
            print(f"{table} is not in database or does not have title column")
            exit()
            
        # fetch all titles, use list comprehension to select only the first element since a tuple is returned by .fetchall
        titles = cur.fetchall()
        titles = [title[0] for title in titles]
        
        # loop through each title pulled
        # turn the string into a list of each word with punctuation stripped
        # extend the list of title words to the overall word list
        for title in titles:
            title_words = re.findall(r"\w+'*\w*", title)
            title_words = [word.lower() for word in title_words]
            print(title_words)
            words.extend(title_words)
    # return the word list of all title words
    return words

# calculate word frequency
# input: words (list of all words -- return value from get_words_from_database)
# output: word_dict (a dictionary; key = word, value = its frequency within the words list)
def calculate_word_frequency(words):
    
    # initialize empty dictionary
    word_dict = {}
    
    # if there are words in the list, iterate through each one
    if words:
        for word in words:
            # if word not in the word_dictionary and it is not a preposition/common word...
            # make dictionary key and set value to zero
            # update key's value to be +1
            if word not in word_dict:
                if word in STOPWORDS:
                    continue
                else:
                    word_dict[word] = 0
            word_dict[word] += 1
        # return word_dict or exit function if words list is empty
        return word_dict
    else:
        print("No word frequencies to calculate")
        exit()

# write calculations to csv file
# input: filename (name of the csv file to write to)
# input: word_dict (dictionary with keys = words and values = word frequency in titles; returned value from calculate_word_frequency)
# input: table_names_lst (list of table names to get title information from; initialized in main)
# output: table_names_string (a string version of the table names list, each table seperated with a comma)
# output: table (a string of either "table" or "tables" depending on length of table_names_lst)
def write_to_csv_file(filename, word_dict, table_names_lst):
    
    # if word_dict is empty, exit program
    if not word_dict:
        print("no word frequencies in dictionary")
        exit()
        
    # determine value for table/s based on how many table names in lst 
    if len(table_names_lst) > 1:
        table = "tables"
    else:
        table = "table"
    
    # create string version of table names lst for easy writing to csv file
    table_names_string = ', '.join(table_names_lst)
    
    # sort the dictionary items by frequency in descending order
    # turn the list of tuples into a list of lists (for easier conversion in csv file writing)
    sorted_tuples = sorted(word_dict.items(), key=lambda x: x[1], reverse=True)
    sorted_list = [list(tuple) for tuple in sorted_tuples]

    # open a csv file writer
    file = open(filename, 'w')
    csv_writer = csv.writer(file)
    
    # write file header and column names
    csv_writer.writerow([f"Frequency of Artwork Title Words From the {table_names_string} {table}: Top 20 Words"])
    csv_writer.writerow(['Word', 'Frequency'])
    
    # write a row for each word, frequency pair in list of words
    csv_writer.writerows(sorted_list[:20])
    
    # close the file
    file.close()
    return table_names_string, table

# make the word cloud based on word frequencies
# input: word_dict (dictionary of words and frequencies -- returned value from calculate_word_frequencies)
# input: table_names_string (a string version of the table names list, each table seperated with a comma -- returned from write_to_csv_file)
# input: table (a string of either "table" or "tables" depending on length of table_names_lst -- returned from write_to_csv_file)
# output: png file of wordcloud
def visualize_word_cloud(word_dict, table_names_string, table):
    
    # if word_dict is full, make a word cloud
    if word_dict:
        
        # set width, height, and bg color, generate from word_dict frequencies
        word_cloud = WordCloud(width=1000, height=500, background_color='white').generate_from_frequencies(frequencies=word_dict)
        
        # create the figure
        plt.figure(figsize=(10, 5))
        plt.imshow(word_cloud, interpolation="bicubic")
        
        # create title, turn off axis, save figure as png
        plt.title(f"Frequency of Artwork Title Words From the {table_names_string} {table.capitalize()}: All Words")
        plt.axis("off")
        
        plt.tight_layout()
        
        plt.savefig("allsources_wordcloud_of_title_words.png")
        
        
        # show the figure
        plt.show()
    
    # if word_dict is empty, exit the program
    else:
        print("No data to display")
        exit()
    
def main():
    table_names_lst = ['Open_Library', 'Cleveland', 'Harvard', 'Met']
    words_lst = get_words_from_database(table_names_lst, 'Museums.db')
    #print(words_lst)
    words_dict = calculate_word_frequency(words_lst)
    #print(words_dict)
    table_names_string, table = write_to_csv_file('allsources_word_frequencies_in_titles.csv', words_dict, table_names_lst)
    visualize_word_cloud(words_dict, table_names_string, table)

main()


