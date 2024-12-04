import sqlite3
import matplotlib.pyplot as plt
import os

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

def process_data(data, interval=10):
    gender_distribution = {}

    for year, gender_id in data:
        interval_key = (year // interval) * interval
        if interval_key not in gender_distribution:
            gender_distribution[interval_key] = {'male': 0, 'female': 0}
        
        if gender_id == 1:
            gender_distribution[interval_key]['female'] += 1
        else:
            gender_distribution[interval_key]['male'] += 1

    return gender_distribution

def write_data_to_text_file(gender_distribution):
    with open("gender_distribution_data.txt", "w") as file:
        file.write("Gender Distribution of Painters Over Time:\n")
        file.write("Interval (Years)\tMale Painters\tFemale Painters\n")
        for interval, counts in sorted(gender_distribution.items()):
            file.write(f"{interval}-{interval + 19}\t{counts['male']}\t{counts['female']}\n")

def plot_gender_distribution(gender_distribution):
    intervals = sorted(gender_distribution.keys())
    male_counts = [gender_distribution[interval]['male'] for interval in intervals]
    female_counts = [gender_distribution[interval]['female'] for interval in intervals]

    plt.figure(figsize=(12, 6))
    plt.bar(intervals, male_counts, width=8, label="Male Painters", alpha=0.7, color="blue")
    plt.bar(intervals, female_counts, width=8, label="Female Painters", alpha=0.7, color="pink", bottom=male_counts)

    plt.xlabel("Year Intervals")
    plt.ylabel("Number of Painters")
    plt.title("Gender Distribution of Painters Over Time")
    plt.legend()
    plt.xticks(intervals, rotation=45)
    plt.tight_layout()

    plt.savefig("gender_distribution_over_time.png")
    plt.show()

def main():
    database_name = "Museums.db"
    data = get_data_from_database(database_name)
    gender_distribution = process_data(data, interval=20)
    
    write_data_to_text_file(gender_distribution)
    
    plot_gender_distribution(gender_distribution)

if __name__ == "__main__":
    main()