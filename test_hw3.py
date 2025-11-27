import mysql.connector
from music_db import (
    clear_database,
    load_single_songs,
    get_most_prolific_individual_artists
)

# Connect to MySQL using mysql.connector
mydb = mysql.connector.connect(
    host="localhost",
    user="gt360",         # your MySQL username
    password="mypassword",   # your MySQL password
    database="musicdb"
)

# Test 1: clear DB
clear_database(mydb)
print("DB cleared.")

# Test 2: insert sample single songs
sample_singles = [
    ("Hello", ("Pop",), "Adele", "2015-10-01"),
    ("Skyfall", ("Pop",), "Adele", "2012-10-01"),
    ("Bad Habits", ("Pop", "Electronic"), "Ed Sheeran", "2021-07-01"),
]

rejects = load_single_songs(mydb, sample_singles)
print("Rejected:", rejects)

# Test 3: query
results = get_most_prolific_individual_artists(mydb, 5, (2000, 2025))
print("Most prolific:", results)