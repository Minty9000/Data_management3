import mysql.connector
from music_db import *

# Connect to MySQL
mydb = mysql.connector.connect(
    host="localhost",
    user="mk2605",         # Change to your MySQL username
    password="mypassword",   # Change to your MySQL password
    database="musicdb"
)

cursor = mydb.cursor()

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BOLD = '\033[1m'
END = '\033[0m'

test_count = 0
passed_count = 0

def assert_equal(actual, expected, test_name):
    global test_count, passed_count
    test_count += 1
    if actual == expected:
        passed_count += 1
        print(f"{GREEN}✓{END} {test_name}")
        return True
    else:
        print(f"{RED}✗{END} {test_name}")
        print(f"  Expected: {expected}")
        print(f"  Got:      {actual}")
        return False

def assert_true(condition, test_name):
    global test_count, passed_count
    test_count += 1
    if condition:
        passed_count += 1
        print(f"{GREEN}✓{END} {test_name}")
        return True
    else:
        print(f"{RED}✗{END} {test_name}")
        return False

def assert_false(condition, test_name):
    global test_count, passed_count
    test_count += 1
    if not condition:
        passed_count += 1
        print(f"{GREEN}✓{END} {test_name}")
        return True
    else:
        print(f"{RED}✗{END} {test_name}")
        return False

def get_table_count(table_name):
    """Helper to get row count from a table"""
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    return cursor.fetchone()[0]

print("=" * 80)
print(f"{BOLD}COMPREHENSIVE MUSIC DATABASE TEST SUITE{END}")
print("=" * 80)

# ============================================================================
# PART 0: SCHEMA VALIDATION
# ============================================================================
print(f"\n{BOLD}[PART 0] SCHEMA VALIDATION{END}")
print("-" * 80)

# Check all tables exist (7 tables only - no SongArtist)
tables_to_check = ["Artist", "Genre", "Album", "Song", "SongGenre", "User", "Rating"]
for table in tables_to_check:
    cursor.execute(f"SELECT 1 FROM information_schema.tables WHERE table_name='{table}' AND table_schema='musicdb'")
    assert_true(cursor.fetchone() is not None, f"Table '{table}' exists")

print()

# ============================================================================
# PART 1: CLEAR DATABASE
# ============================================================================
print(f"{BOLD}[PART 1] CLEAR DATABASE{END}")
print("-" * 80)

clear_database(mydb)

for table in ["Rating", "SongGenre", "Song", "Album", "User", "Artist", "Genre"]:
    count = get_table_count(table)
    assert_equal(count, 0, f"Table '{table}' is empty after clear_database()")

print()

# ============================================================================
# PART 2: LOAD SINGLE SONGS
# ============================================================================
print(f"{BOLD}[PART 2] LOAD SINGLE SONGS{END}")
print("-" * 80)

sample_singles = [
    ("Hello", ("Pop",), "Adele", "2015-10-01"),
    ("Skyfall", ("Pop",), "Adele", "2012-10-01"),
    ("Bad Habits", ("Pop", "Electronic"), "Ed Sheeran", "2021-07-01"),
    ("Shape of You", ("Pop",), "Ed Sheeran", "2017-01-06"),
    ("Rolling in the Deep", ("Pop", "Soul"), "Adele", "2010-11-29"),
    ("Bohemian Rhapsody", ("Rock", "Pop"), "Queen", "1975-10-31"),
]

rejects = load_single_songs(mydb, sample_singles)
assert_equal(len(rejects), 0, "No singles rejected on first load")
assert_equal(get_table_count("Song"), 6, "6 songs inserted")
assert_equal(get_table_count("Artist"), 3, "3 artists auto-created")
assert_equal(get_table_count("Genre"), 4, "4 genres auto-created (Pop, Electronic, Soul, Rock)")

# Test SongGenre population (not SongArtist - that table doesn't exist)
# Songs: Hello(1), Skyfall(1), Bad Habits(2), Shape of You(1), Rolling in the Deep(2), Bohemian Rhapsody(2) = 9 total
cursor.execute("SELECT COUNT(*) FROM SongGenre")
songgenre_count = cursor.fetchone()[0]
assert_equal(songgenre_count, 9, "All songs have genre entries in SongGenre")

# Test duplicate rejection
duplicate_singles = [("Hello", ("Pop",), "Adele", "2015-10-01")]
rejects = load_single_songs(mydb, duplicate_singles)
assert_equal(len(rejects), 1, "Duplicate single rejected")
assert_equal(get_table_count("Song"), 6, "No new song added (still 6 total)")

# Test multiple genres linked correctly
cursor.execute("""
    SELECT COUNT(*) FROM SongGenre sg
    JOIN Song s ON sg.song_id = s.song_id
    WHERE s.title = 'Bad Habits' AND s.artist_name = 'Ed Sheeran'
""")
bad_habits_genres = cursor.fetchone()[0]
assert_equal(bad_habits_genres, 2, "Bad Habits linked to 2 genres (Pop, Electronic)")

# Test case preservation
cursor.execute("SELECT artist_name FROM Song WHERE title = 'Hello' LIMIT 1")
result = cursor.fetchone()
if result:
    assert_true(result[0] == "Adele", "Artist name case preserved")

print()

# ============================================================================
# PART 3: LOAD ALBUMS
# ============================================================================
print(f"{BOLD}[PART 3] LOAD ALBUMS{END}")
print("-" * 80)

clear_database(mydb)

# First load singles to test album + single artist
sample_singles_for_album = [
    ("Standalone Single 1", ("Pop",), "Adele", "2015-10-01"),
    ("Standalone Single 2", ("Pop",), "Ed Sheeran", "2017-01-06"),
]
load_single_songs(mydb, sample_singles_for_album)

albums = [
    ("25", "Pop", "Adele", "2015-11-20", ["Album Track 1", "Album Track 2", "Album Track 3"]),
    ("÷", "Pop", "Ed Sheeran", "2017-03-03", ["Shape of You", "Galway Girl", "Perfect"]),
    ("21", "Soul", "Adele", "2011-01-24", ["Rolling in the Deep", "Someone Like You", "Set Fire to the Rain"]),
]

album_rejects = load_albums(mydb, albums)
assert_equal(len(album_rejects), 0, "No albums rejected on first load")
assert_equal(get_table_count("Album"), 3, "3 albums inserted")

# Check songs in albums
cursor.execute("SELECT COUNT(*) FROM Song WHERE album_id IS NOT NULL")
album_songs = cursor.fetchone()[0]
assert_equal(album_songs, 9, "9 album songs inserted (3 per album)")

# Test SongGenre population for album songs
cursor.execute("SELECT COUNT(*) FROM SongGenre WHERE song_id IN (SELECT song_id FROM Song WHERE album_id IS NOT NULL)")
album_songgenre_count = cursor.fetchone()[0]
assert_equal(album_songgenre_count, 9, "All 9 album songs have SongGenre entries")

# Test duplicate album rejection (same title + artist)
duplicate_album = [
    ("25", "Pop", "Adele", "2015-11-20", ["Duplicate Song"]),
]
album_rejects = load_albums(mydb, duplicate_album)
assert_equal(len(album_rejects), 1, "Duplicate album rejected")

# Test genre linking to album songs
cursor.execute("""
    SELECT COUNT(DISTINCT sg.genre_id) FROM SongGenre sg
    JOIN Song s ON sg.song_id = s.song_id
    WHERE s.album_id IN (SELECT album_id FROM Album WHERE title = '25')
""")
genre_count = cursor.fetchone()[0]
assert_equal(genre_count, 1, "All songs in album 25 linked to 1 genre (Pop)")

# Test that song can exist in album even if it was a single (different artist is OK)
sample_new_single = [("Someone Like You", ("Soul",), "Someone Artist", "2011-01-24")]
rejects = load_single_songs(mydb, sample_new_single)
# This should be accepted because it's by a different artist
assert_equal(len(rejects), 0, "Same song title by different artist is accepted")

print()

# ============================================================================
# PART 4: LOAD USERS
# ============================================================================
print(f"{BOLD}[PART 4] LOAD USERS{END}")
print("-" * 80)

clear_database(mydb)

users = ["alice", "bob", "charlie", "diana", "eve"]
user_rejects = load_users(mydb, users)
assert_equal(len(user_rejects), 0, "All 5 users added successfully")
assert_equal(get_table_count("User"), 5, "5 users in database")

# Test duplicate rejection
duplicate_users = ["alice", "bob", "frank"]
user_rejects = load_users(mydb, duplicate_users)
assert_equal(len(user_rejects), 2, "2 duplicate users rejected (alice, bob)")
assert_equal(get_table_count("User"), 6, "1 new user added (frank), total 6")

# Test case sensitivity in usernames
case_test_users = ["Alice"]  # Capital A
user_rejects = load_users(mydb, case_test_users)
assert_equal(len(user_rejects), 1, "Username 'Alice' treated as duplicate of 'alice' (MySQL case-insensitive)")

print()

# ============================================================================
# PART 5: LOAD SONG RATINGS
# ============================================================================
print(f"{BOLD}[PART 5] LOAD SONG RATINGS{END}")
print("-" * 80)

clear_database(mydb)

# Setup: Create songs and users
setup_singles = [
    ("Hello", ("Pop",), "Adele", "2015-10-01"),
    ("Shape of You", ("Pop",), "Ed Sheeran", "2017-01-06"),
    ("Bohemian Rhapsody", ("Rock",), "Queen", "1975-10-31"),
]
load_single_songs(mydb, setup_singles)

setup_users = ["alice", "bob", "charlie"]
load_users(mydb, setup_users)

# Valid ratings
valid_ratings = [
    ("alice", ("Adele", "Hello"), 5, "2023-01-15"),
    ("bob", ("Ed Sheeran", "Shape of You"), 4, "2023-02-20"),
    ("charlie", ("Queen", "Bohemian Rhapsody"), 5, "2023-03-10"),
    ("alice", ("Ed Sheeran", "Shape of You"), 3, "2023-04-05"),
    ("bob", ("Queen", "Bohemian Rhapsody"), 2, "2023-05-12"),
]
rating_rejects = load_song_ratings(mydb, valid_ratings)
assert_equal(len(rating_rejects), 0, "All 5 valid ratings accepted")
assert_equal(get_table_count("Rating"), 5, "5 ratings in database")

# Test invalid rating values (out of 1-5 range)
invalid_value_ratings = [
    ("charlie", ("Adele", "Hello"), 0, "2023-06-01"),  # 0 is invalid
]
rating_rejects = load_song_ratings(mydb, invalid_value_ratings)
assert_equal(len(rating_rejects), 1, "Out-of-range rating (0) rejected")

invalid_value_ratings_2 = [
    ("charlie", ("Adele", "Hello"), 6, "2023-06-01"),  # 6 is invalid
]
rating_rejects = load_song_ratings(mydb, invalid_value_ratings_2)
assert_equal(len(rating_rejects), 1, "Out-of-range rating (6) rejected")

# Test non-existent user
non_user_rating = [("nonexistent", ("Adele", "Hello"), 5, "2023-06-15")]
rating_rejects = load_song_ratings(mydb, non_user_rating)
assert_equal(len(rating_rejects), 1, "Rating from non-existent user rejected")

# Test non-existent song
non_song_rating = [("alice", ("Adele", "Nonexistent Song"), 5, "2023-06-15")]
rating_rejects = load_song_ratings(mydb, non_song_rating)
assert_equal(len(rating_rejects), 1, "Rating for non-existent song rejected")

# Test duplicate rating (same user, same song)
duplicate_rating = [("alice", ("Adele", "Hello"), 4, "2023-07-01")]
rating_rejects = load_song_ratings(mydb, duplicate_rating)
assert_equal(len(rating_rejects), 1, "Duplicate rating (alice rating Hello again) rejected")

print()

# ============================================================================
# PART 6: GET MOST PROLIFIC INDIVIDUAL ARTISTS
# ============================================================================
print(f"{BOLD}[PART 6] GET MOST PROLIFIC INDIVIDUAL ARTISTS{END}")
print("-" * 80)

clear_database(mydb)

# Create singles with specific years
prolific_singles = [
    ("Single 2019 A", ("Pop",), "Adele", "2019-01-01"),
    ("Single 2020 A", ("Pop",), "Adele", "2020-01-01"),
    ("Single 2021 A", ("Pop",), "Adele", "2021-01-01"),
    ("Single 2021 B", ("Pop",), "Ed Sheeran", "2021-01-01"),
    ("Single 2021 C", ("Pop",), "Ed Sheeran", "2021-01-01"),
    ("Single 2022 A", ("Pop",), "Ed Sheeran", "2022-01-01"),
    ("Single 2023 A", ("Pop",), "Queen", "2023-01-01"),
]
load_single_songs(mydb, prolific_singles)

# Test 1: Year range includes all
result = get_most_prolific_individual_artists(mydb, 10, (2019, 2023))
assert_equal(len(result), 3, "3 artists returned for year range 2019-2023")
assert_equal(result[0][0], "Adele", "Adele is most prolific (3 singles)")
assert_equal(result[0][1], 3, "Adele has 3 singles")
assert_equal(result[1][0], "Ed Sheeran", "Ed Sheeran is second (3 singles)")
assert_equal(result[1][1], 3, "Ed Sheeran has 3 singles")
assert_equal(result[2][0], "Queen", "Queen is third (1 single)")
assert_equal(result[2][1], 1, "Queen has 1 single")

# Test 2: Year range 2021 only
result = get_most_prolific_individual_artists(mydb, 10, (2021, 2021))
assert_equal(len(result), 2, "2 artists have singles in 2021 only")
assert_equal(result[0][0], "Ed Sheeran", "Ed Sheeran has 2 singles in 2021 (most prolific)")
assert_equal(result[0][1], 2, "Ed Sheeran has 2 singles in 2021")
assert_equal(result[1][0], "Adele", "Adele has 1 single in 2021")
assert_equal(result[1][1], 1, "Adele has 1 single in 2021")

# Test 3: Top N limiting
result = get_most_prolific_individual_artists(mydb, 2, (2019, 2023))
assert_equal(len(result), 2, "Limiting to top 2 returns 2 artists")

# Test 4: Empty year range
result = get_most_prolific_individual_artists(mydb, 10, (2025, 2025))
assert_equal(len(result), 0, "No artists in year 2025")

# Test 5: Alphabetical tie-breaking
tie_singles = [
    ("Tie Single 1", ("Pop",), "Zara", "2023-01-01"),
    ("Tie Single 2", ("Pop",), "Alice", "2023-01-01"),
]
load_single_songs(mydb, tie_singles)
result = get_most_prolific_individual_artists(mydb, 10, (2023, 2023))
tie_results = [r for r in result if r[0] in ["Alice", "Zara"]]
assert_true(tie_results[0][0] < tie_results[1][0], "Alphabetical order for ties (Alice before Zara)")

print()

# ============================================================================
# PART 7: GET ARTISTS LAST SINGLE IN YEAR
# ============================================================================
print(f"{BOLD}[PART 7] GET ARTISTS LAST SINGLE IN YEAR{END}")
print("-" * 80)

clear_database(mydb)

year_singles = [
    ("Single 2020", ("Pop",), "Adele", "2020-01-01"),
    ("Single 2021", ("Pop",), "Adele", "2021-12-31"),
    ("Single 2020 A", ("Pop",), "Ed Sheeran", "2020-01-01"),
    ("Single 2020 B", ("Pop",), "Ed Sheeran", "2020-06-01"),
    ("Single 2023", ("Pop",), "Queen", "2023-05-01"),
]
load_single_songs(mydb, year_singles)

# Test 1: Last single in 2021 (Adele only)
result = get_artists_last_single_in_year(mydb, 2021)
assert_equal(result, {"Adele"}, "Only Adele's last single is in 2021")

# Test 2: Last single in 2020 (Ed Sheeran only)
result = get_artists_last_single_in_year(mydb, 2020)
assert_equal(result, {"Ed Sheeran"}, "Only Ed Sheeran's last single is in 2020")

# Test 3: Last single in 2023 (Queen only)
result = get_artists_last_single_in_year(mydb, 2023)
assert_equal(result, {"Queen"}, "Only Queen's last single is in 2023")

# Test 4: Year with no artists' last single
result = get_artists_last_single_in_year(mydb, 2019)
assert_equal(result, set(), "Empty set for year with no artist's last single")

# Test 5: Multiple artists with last single in same year
multi_year_singles = [
    ("Single 2024 A", ("Pop",), "Zara", "2024-01-01"),
    ("Single 2024 B", ("Pop",), "Frank", "2024-06-01"),
]
load_single_songs(mydb, multi_year_singles)
result = get_artists_last_single_in_year(mydb, 2024)
assert_equal(result, {"Zara", "Frank"}, "Both Zara and Frank have last singles in 2024")

print()

# ============================================================================
# PART 8: GET TOP SONG GENRES
# ============================================================================
print(f"{BOLD}[PART 8] GET TOP SONG GENRES{END}")
print("-" * 80)

clear_database(mydb)

# Create songs with varying genre distributions
genre_singles = [
    ("Pop 1", ("Pop",), "Artist1", "2020-01-01"),
    ("Pop 2", ("Pop",), "Artist2", "2020-01-02"),
    ("Pop 3", ("Pop",), "Artist3", "2020-01-03"),
    ("Pop 4", ("Pop",), "Artist4", "2020-01-04"),
    ("Pop 5", ("Pop",), "Artist5", "2020-01-05"),
    ("Rock 1", ("Rock",), "Artist6", "2020-01-06"),
    ("Rock 2", ("Rock",), "Artist7", "2020-01-07"),
    ("Rock 3", ("Rock",), "Artist8", "2020-01-08"),
    ("Jazz 1", ("Jazz",), "Artist9", "2020-01-09"),
]
load_single_songs(mydb, genre_singles)

# Test 1: Top 3 genres
result = get_top_song_genres(mydb, 3)
assert_equal(len(result), 3, "Top 3 genres returned")
assert_equal(result[0][0], "Pop", "Pop is #1 genre (5 songs)")
assert_equal(result[0][1], 5, "Pop has 5 songs")
assert_equal(result[1][0], "Rock", "Rock is #2 genre (3 songs)")
assert_equal(result[1][1], 3, "Rock has 3 songs")
assert_equal(result[2][0], "Jazz", "Jazz is #3 genre (1 song)")
assert_equal(result[2][1], 1, "Jazz has 1 song")

# Test 2: Top 1 genre
result = get_top_song_genres(mydb, 1)
assert_equal(len(result), 1, "Top 1 genre returned")
assert_equal(result[0][0], "Pop", "Pop is top genre")

# Test 3: Alphabetical tie-breaking
tie_genres = [
    ("Zed Song", ("Zgenre",), "Artist10", "2020-01-10"),
    ("Aff Song", ("Agenre",), "Artist11", "2020-01-11"),
]
load_single_songs(mydb, tie_genres)
result = get_top_song_genres(mydb, 10)
one_song_genres = [r for r in result if r[1] == 1 and r[0] in ["Agenre", "Zgenre"]]
if len(one_song_genres) >= 2:
    assert_true(one_song_genres[0][0] < one_song_genres[1][0], "Alphabetical order for tie (Agenre before Zgenre)")

print()

# ============================================================================
# PART 9: GET ALBUM AND SINGLE ARTISTS
# ============================================================================
print(f"{BOLD}[PART 9] GET ALBUM AND SINGLE ARTISTS{END}")
print("-" * 80)

clear_database(mydb)

# Artist 1: Only singles
load_single_songs(mydb, [("Single Only 1", ("Pop",), "SingleOnly", "2020-01-01")])

# Artist 2: Album + single
load_single_songs(mydb, [("Single Mixed 1", ("Pop",), "Mixed", "2020-01-01")])
load_albums(mydb, [("Album Mixed", "Pop", "Mixed", "2020-02-01", ["Song in Album"])])

# Artist 3: Only albums
load_albums(mydb, [("Album Only", "Pop", "AlbumOnly", "2020-03-01", ["Song in Album Only"])])

result = get_album_and_single_artists(mydb)
assert_equal(result, {"Mixed"}, "Only Mixed artist has both albums and singles")

# Test 2: Multiple artists with both
load_albums(mydb, [("Album Another", "Pop", "SingleOnly", "2020-04-01", ["Song X"])])
result = get_album_and_single_artists(mydb)
assert_equal(result, {"Mixed", "SingleOnly"}, "Both Mixed and SingleOnly have albums and singles")

print()

# ============================================================================
# PART 10: GET MOST RATED SONGS
# ============================================================================
print(f"{BOLD}[PART 10] GET MOST RATED SONGS{END}")
print("-" * 80)

clear_database(mydb)

# Setup
rated_singles = [
    ("Song A", ("Pop",), "Artist1", "2023-01-01"),
    ("Song B", ("Pop",), "Artist2", "2023-01-02"),
    ("Song C", ("Pop",), "Artist3", "2023-01-03"),
    ("Song D", ("Pop",), "Artist4", "2022-01-01"),
]
load_single_songs(mydb, rated_singles)

rated_users = ["user1", "user2", "user3", "user4", "user5"]
load_users(mydb, rated_users)

# Load ratings
ratings = [
    ("user1", ("Artist1", "Song A"), 5, "2023-02-01"),
    ("user2", ("Artist1", "Song A"), 4, "2023-02-02"),
    ("user3", ("Artist1", "Song A"), 3, "2023-02-03"),
    ("user4", ("Artist2", "Song B"), 5, "2023-03-01"),
    ("user5", ("Artist2", "Song B"), 4, "2023-03-02"),
    ("user1", ("Artist3", "Song C"), 5, "2023-04-01"),
    ("user2", ("Artist4", "Song D"), 5, "2022-05-01"),
]
load_song_ratings(mydb, ratings)

# Test 1: Year range 2023
result = get_most_rated_songs(mydb, (2023, 2023), 10)
assert_equal(len(result), 3, "3 songs were rated in 2023")
assert_equal(result[0][0], "Song A", "Song A has most ratings in 2023 (3)")
assert_equal(result[0][1], "Artist1", "Song A is by Artist1")
assert_equal(result[0][2], 3, "Song A has 3 ratings")
assert_equal(result[1][0], "Song B", "Song B has second-most ratings (2)")
assert_equal(result[1][2], 2, "Song B has 2 ratings")

# Test 2: Year range 2022
result = get_most_rated_songs(mydb, (2022, 2022), 10)
assert_equal(len(result), 1, "Only Song D was rated in 2022")
assert_equal(result[0][0], "Song D", "Song D is in 2022")

# Test 3: Top N limiting
result = get_most_rated_songs(mydb, (2023, 2023), 1)
assert_equal(len(result), 1, "Top 1 returns 1 song")
assert_equal(result[0][0], "Song A", "Top song is Song A")

# Test 4: Alphabetical tie-breaking
tie_ratings = [
    ("user1", ("Artist5", "Zebra Song"), 5, "2023-06-01"),
    ("user2", ("Artist6", "Apple Song"), 5, "2023-06-01"),
]
load_song_ratings(mydb, tie_ratings)
result = get_most_rated_songs(mydb, (2023, 2023), 10)
one_rated = [r for r in result if r[2] == 1 and r[0] in ["Zebra Song", "Apple Song"]]
if len(one_rated) >= 2:
    assert_true(one_rated[0][0] < one_rated[1][0], "Alphabetical order for ties (Apple before Zebra)")

print()

# ============================================================================
# PART 11: GET MOST ENGAGED USERS
# ============================================================================
print(f"{BOLD}[PART 11] GET MOST ENGAGED USERS{END}")
print("-" * 80)

clear_database(mydb)

# Setup
engaged_singles = [
    ("Song 1", ("Pop",), "Artist1", "2023-01-01"),
    ("Song 2", ("Pop",), "Artist2", "2023-01-02"),
    ("Song 3", ("Pop",), "Artist3", "2023-01-03"),
    ("Song 4", ("Pop",), "Artist4", "2023-01-04"),
    ("Song 5", ("Pop",), "Artist5", "2023-01-05"),
    ("Song 6", ("Pop",), "Artist1", "2022-01-01"),
]
load_single_songs(mydb, engaged_singles)

engaged_users = ["alice", "bob", "charlie", "diana"]
load_users(mydb, engaged_users)

# Load ratings with different engagement levels
engagement_ratings = [
    ("alice", ("Artist1", "Song 1"), 5, "2023-02-01"),
    ("alice", ("Artist2", "Song 2"), 4, "2023-02-02"),
    ("alice", ("Artist3", "Song 3"), 3, "2023-02-03"),
    ("bob", ("Artist1", "Song 1"), 5, "2023-03-01"),
    ("bob", ("Artist2", "Song 2"), 4, "2023-03-02"),
    ("charlie", ("Artist1", "Song 1"), 5, "2023-04-01"),
    ("alice", ("Artist1", "Song 6"), 5, "2022-05-01"),
]
load_song_ratings(mydb, engagement_ratings)

# Test 1: Year range 2023
result = get_most_engaged_users(mydb, (2023, 2023), 10)
assert_equal(len(result), 3, "3 users rated in 2023")
assert_equal(result[0][0], "alice", "Alice is most engaged in 2023 (3 ratings)")
assert_equal(result[0][1], 3, "Alice has 3 ratings")
assert_equal(result[1][0], "bob", "Bob is second (2 ratings)")
assert_equal(result[1][1], 2, "Bob has 2 ratings")
assert_equal(result[2][0], "charlie", "Charlie is third (1 rating)")
assert_equal(result[2][1], 1, "Charlie has 1 rating")

# Test 2: Year range 2022
result = get_most_engaged_users(mydb, (2022, 2022), 10)
assert_equal(len(result), 1, "Only alice rated in 2022")
assert_equal(result[0][0], "alice", "Alice rated in 2022")

# Test 3: Top N limiting
result = get_most_engaged_users(mydb, (2023, 2023), 1)
assert_equal(len(result), 1, "Top 1 returns 1 user")
assert_equal(result[0][0], "alice", "Top user is alice")

# Test 4: Alphabetical tie-breaking
tie_engagement_ratings = [
    ("zoe", ("Artist1", "Song 4"), 5, "2023-06-01"),
    ("alex", ("Artist2", "Song 5"), 5, "2023-06-01"),
]
load_users(mydb, ["zoe", "alex"])
load_song_ratings(mydb, tie_engagement_ratings)
result = get_most_engaged_users(mydb, (2023, 2023), 10)
one_rated = [r for r in result if r[1] == 1 and r[0] in ["alex", "zoe"]]
if len(one_rated) >= 2:
    assert_true(one_rated[0][0] < one_rated[1][0], "Alphabetical order for ties (alex before zoe)")

print()

# ============================================================================
# PART 12: FOREIGN KEY CONSTRAINT TESTS
# ============================================================================
print(f"{BOLD}[PART 12] FOREIGN KEY CONSTRAINT TESTS{END}")
print("-" * 80)

clear_database(mydb)

# Test 1: Cannot insert rating with non-existent user
load_single_songs(mydb, [("Test Song", ("Pop",), "Test Artist", "2023-01-01")])
invalid_rating = [("nonexistent_user", ("Test Artist", "Test Song"), 5, "2023-01-01")]
rejects = load_song_ratings(mydb, invalid_rating)
assert_equal(len(rejects), 1, "Rating with non-existent user rejected")

# Test 2: Cannot insert rating with non-existent song
load_users(mydb, ["valid_user"])
invalid_rating = [("valid_user", ("Test Artist", "Nonexistent Song"), 5, "2023-01-01")]
rejects = load_song_ratings(mydb, invalid_rating)
assert_equal(len(rejects), 1, "Rating for non-existent song rejected")

# Test 3: Delete artist cascades to songs
cursor.execute("SELECT COUNT(*) FROM Song WHERE artist_name = 'Test Artist'")
before_delete = cursor.fetchone()[0]
assert_true(before_delete > 0, "Song exists before artist deletion")
cursor.execute("DELETE FROM Artist WHERE name = 'Test Artist'")
mydb.commit()
cursor.execute("SELECT COUNT(*) FROM Song WHERE artist_name = 'Test Artist'")
after_delete = cursor.fetchone()[0]
assert_equal(after_delete, 0, "Song cascaded deleted when artist was deleted")

# Test 4: Delete song cascades to ratings
clear_database(mydb)
load_single_songs(mydb, [("Test Song", ("Pop",), "Test Artist", "2023-01-01")])
load_users(mydb, ["test_user"])
load_song_ratings(mydb, [("test_user", ("Test Artist", "Test Song"), 5, "2023-01-01")])
cursor.execute("SELECT COUNT(*) FROM Rating")
before = cursor.fetchone()[0]
cursor.execute("SELECT song_id FROM Song WHERE title = 'Test Song'")
song_id = cursor.fetchone()[0]
cursor.execute("DELETE FROM Song WHERE song_id = %s", (song_id,))
mydb.commit()
cursor.execute("SELECT COUNT(*) FROM Rating WHERE song_id = %s", (song_id,))
after = cursor.fetchone()[0]
assert_equal(after, 0, "Rating cascaded deleted when song was deleted")

print()

# ============================================================================
# PART 13: DATA TYPE AND EDGE CASE TESTS
# ============================================================================
print(f"{BOLD}[PART 13] DATA TYPE AND EDGE CASE TESTS{END}")
print("-" * 80)

clear_database(mydb)

# Test 1: Very long artist name
long_artist = "A" * 150  # Maximum allowed
load_single_songs(mydb, [("Song", ("Pop",), long_artist, "2023-01-01")])
cursor.execute("SELECT COUNT(*) FROM Artist WHERE name = %s", (long_artist,))
assert_equal(cursor.fetchone()[0], 1, "Artist with 150-character name stored correctly")

# Test 2: Very long song title
long_title = "B" * 300  # Maximum allowed
load_single_songs(mydb, [((long_title), ("Pop",), "Artist", "2023-01-01")])
cursor.execute("SELECT COUNT(*) FROM Song WHERE title = %s", (long_title,))
assert_equal(cursor.fetchone()[0], 1, "Song with 300-character title stored correctly")

# Test 3: Date boundaries (leap year, end of month)
edge_dates = [
    ("Song Leap", ("Pop",), "Leap Artist", "2020-02-29"),  # Leap year
    ("Song End Month", ("Pop",), "End Artist", "2023-12-31"),  # End of year
]
load_single_songs(mydb, edge_dates)
cursor.execute("SELECT COUNT(*) FROM Song WHERE release_date IN ('2020-02-29', '2023-12-31')")
assert_equal(cursor.fetchone()[0], 2, "Leap year and year-end dates handled correctly")

# Test 4: Multiple genres on a single song (verify all are linked)
load_single_songs(mydb, [("Multi Genre Song", ("Rock", "Metal", "Heavy Metal"), "Multi Artist", "2023-01-01")])
cursor.execute("""
    SELECT COUNT(DISTINCT genre_id) FROM SongGenre sg
    JOIN Song s ON sg.song_id = s.song_id
    WHERE s.title = 'Multi Genre Song'
""")
assert_equal(cursor.fetchone()[0], 3, "Single song correctly linked to 3 genres")

# Test 5: Album with multiple songs
album_with_multiple = [("Album Multi", "Pop", "Album Artist", "2023-01-01", ["S1", "S2", "S3", "S4", "S5"])]
load_albums(mydb, album_with_multiple)
cursor.execute("SELECT COUNT(*) FROM Song WHERE album_id IN (SELECT album_id FROM Album WHERE title = 'Album Multi')")
assert_equal(cursor.fetchone()[0], 5, "Album with 5 songs all inserted")

print()

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print(f"{BOLD}TEST SUMMARY{END}")
print("=" * 80)
print(f"Total Tests: {test_count}")
print(f"{GREEN}Passed: {passed_count}{END}")
print(f"{RED}Failed: {test_count - passed_count}{END}")

if passed_count == test_count:
    print(f"\n{GREEN}{BOLD}✓ ALL TESTS PASSED!{END}")
else:
    print(f"\n{RED}{BOLD}✗ SOME TESTS FAILED{END}")
    print(f"Success Rate: {(passed_count/test_count)*100:.1f}%")

print("=" * 80)

mydb.close()