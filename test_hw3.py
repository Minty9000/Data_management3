import mysql.connector
from music_db import *

# Connect to MySQL
mydb = mysql.connector.connect(
    host="localhost",
    user="mk2605",         # Change to your MySQL username
    password="mypassword",   # Change to your MySQL password
    database="musicdb"
)

print("=" * 60)
print("MUSIC DATABASE TEST - ALL FUNCTIONS")
print("=" * 60)

# TEST 1: Clear Database
print("\n[TEST 1] Clearing database...")
clear_database(mydb)
print("✓ DB cleared.")

# TEST 2: Load Single Songs
print("\n[TEST 2] Loading single songs...")
sample_singles = [
    ("Hello", ("Pop",), "Adele", "2015-10-01"),
    ("Skyfall", ("Pop",), "Adele", "2012-10-01"),
    ("Bad Habits", ("Pop", "Electronic"), "Ed Sheeran", "2021-07-01"),
    ("Shape of You", ("Pop",), "Ed Sheeran", "2017-01-06"),
    ("Rolling in the Deep", ("Pop", "Soul"), "Adele", "2010-11-29"),
]
rejects = load_single_songs(mydb, sample_singles)
print(f"Rejected: {rejects}")
print(f"✓ Loaded {len(sample_singles) - len(rejects)} singles")

# TEST 3: Get Most Prolific Individual Artists
print("\n[TEST 3] Getting most prolific individual artists (2000-2025)...")
results = get_most_prolific_individual_artists(mydb, 5, (2000, 2025))
print("Most prolific artists:")
for artist, count in results:
    print(f"  - {artist}: {count} singles")

# TEST 4: Get Artists Last Single in Year
print("\n[TEST 4] Getting artists whose last single was in 2021...")
artists_2021 = get_artists_last_single_in_year(mydb, 2021)
print(f"Artists with last single in 2021: {artists_2021}")

# TEST 5: Load Albums
print("\n[TEST 5] Loading albums...")
albums = [
    ("25", "Pop", "Adele", "2015-11-20", ["Hello", "I Miss You"]),
    ("÷", "Pop", "Ed Sheeran", "2017-03-03", ["Shape of You", "Galway Girl"]),
    ("21", "Soul", "Adele", "2011-01-24", ["Rolling in the Deep", "Someone Like You"]),
]
album_rejects = load_albums(mydb, albums)
print(f"Album rejects: {album_rejects}")
print(f"✓ Loaded {len(albums) - len(album_rejects)} albums")

# TEST 6: Get Top Song Genres
print("\n[TEST 6] Getting top 3 genres by song count...")
top_genres = get_top_song_genres(mydb, 3)
print("Top genres:")
for genre, count in top_genres:
    print(f"  - {genre}: {count} songs")

# TEST 7: Get Album and Single Artists
print("\n[TEST 7] Getting artists with both albums and singles...")
dual_artists = get_album_and_single_artists(mydb)
print(f"Artists with both albums and singles: {dual_artists}")

# TEST 8: Load Users
print("\n[TEST 8] Loading users...")
users = ["alice", "bob", "charlie", "alice"]  # alice duplicated to test rejection
user_rejects = load_users(mydb, users)
print(f"User rejects (duplicates): {user_rejects}")
print(f"✓ Loaded {len(set(users)) - len(user_rejects)} unique users")

# TEST 9: Load Song Ratings
print("\n[TEST 9] Loading song ratings...")
song_ratings = [
    ("alice", ("Adele", "Hello"), 5, "2023-01-15"),
    ("bob", ("Ed Sheeran", "Shape of You"), 4, "2023-02-20"),
    ("charlie", ("Adele", "Rolling in the Deep"), 5, "2023-03-10"),
    ("alice", ("Ed Sheeran", "Bad Habits"), 3, "2023-04-05"),
    ("bob", ("Adele", "Skyfall"), 4, "2023-05-12"),
    ("charlie", ("Ed Sheeran", "Shape of You"), 5, "2023-06-18"),
]
rating_rejects = load_song_ratings(mydb, song_ratings)
print(f"Rating rejects: {rating_rejects}")
print(f"✓ Loaded {len(song_ratings) - len(rating_rejects)} ratings")

# TEST 10: Get Most Rated Songs
print("\n[TEST 10] Getting top 5 most rated songs (2023)...")
most_rated = get_most_rated_songs(mydb, (2023, 2023), 5)
print("Most rated songs:")
for title, artist, count in most_rated:
    print(f"  - {title} by {artist}: {count} ratings")

# TEST 11: Get Most Engaged Users
print("\n[TEST 11] Getting top 3 most engaged users (2023)...")
engaged_users = get_most_engaged_users(mydb, (2023, 2023), 3)
print("Most engaged users:")
for username, count in engaged_users:
    print(f"  - {username}: {count} ratings")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED")
print("=" * 60)

mydb.close()