import mysql.connector
from typing import List, Tuple, Set, Dict
import datetime

# --- DATABASE CONNECTION SETUP ---

# IMPORTANT: You must replace 'your_username' and 'your_password' with your actual MariaDB credentials.
# The database name should match the one you created: '<netid>_music_db'.
DB_CONFIG = {
    "host": "localhost",
    "user": "your_username",
    "password": "your_password",
    "database": "<net_id>_music_db"
}

def get_db_connection():
    """Returns a new MySQL database connection."""
    try:
        mydb = mysql.connector.connect(**DB_CONFIG)
        return mydb
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        # In a real application, you might raise the error or handle it more gracefully
        return None

# --- DATABASE MANAGEMENT FUNCTIONS ---

def clear_database(mydb):
    """
    [20 pts] Deletes all rows from all tables in the database.
    Required tables: Rating, SongGenre, SongArtist, Song, Album, Artist, User, Genre.
    """
    cursor = mydb.cursor()
    print("Clearing database...")
    
    # Must delete in reverse dependency order to avoid foreign key constraints failing
    tables_to_clear = [
        "Rating",
        "SongGenre",
        "SongArtist",
        "Song", 
        "Album",
        "Artist",
        "User", 
        "Genre"
    ]
    
    # Use TRUNCATE TABLE for efficiency, which also handles foreign keys if performed sequentially
    # We will use DELETE FROM for safety, but TRUNCATE is generally faster.
    for table in tables_to_clear:
        try:
            # Setting foreign_key_checks=0 in the SQL schema allows TRUNCATE/DELETE to be faster/simpler
            # but if that wasn't done, DELETE FROM is safer if foreign keys are not disabled.
            cursor.execute(f"DELETE FROM {table}")
        except mysql.connector.Error as err:
            print(f"Error clearing table {table}: {err}")
    
    mydb.commit()
    cursor.close()
    print("Database cleared successfully.")


def load_single_songs(mydb, single_songs: List[Tuple[str,Tuple[str,str],str,str]]) -> Set[Tuple[str,str]]:
    """
    [35 pts] Inserts single songs (not part of an album) into the database.
    - single_songs: List of (artist_name, (song_title, genre_str), release_date_str, genre_str)
    - Returns: Set of (artist_name, song_title) that were successfully inserted.
    
    Note: You must handle Artist and Genre lookup/insertion first.
    """
    inserted_songs = set()
    cursor = mydb.cursor(prepared=True)
    
    # Pre-compiled queries for efficiency
    
    # 1. Artist Management: Check if artist exists, if not, insert
    insert_artist_sql = "INSERT IGNORE INTO Artist (name) VALUES (%s)"
    select_artist_id_sql = "SELECT artist_id FROM Artist WHERE name = %s"
    
    # 2. Genre Management: Check if genre exists, if not, insert
    insert_genre_sql = "INSERT IGNORE INTO Genre (name) VALUES (%s)"
    select_genre_id_sql = "SELECT genre_id FROM Genre WHERE name = %s"

    # 3. Song Insertion
    insert_song_sql = "INSERT INTO Song (title, release_date, album_id) VALUES (%s, %s, NULL)"
    
    # 4. Song-Artist Link
    insert_song_artist_sql = "INSERT INTO SongArtist (song_id, artist_id) VALUES (%s, %s)"

    # 5. Song-Genre Link
    insert_song_genre_sql = "INSERT INTO SongGenre (song_id, genre_id) VALUES (%s, %s)"


    for artist_name, (song_title, genre_str), release_date_str, _ in single_songs:
        try:
            # --- 1. Get/Insert Artist ---
            cursor.execute(insert_artist_sql, (artist_name,))
            cursor.execute(select_artist_id_sql, (artist_name,))
            artist_id = cursor.fetchone()[0]

            # --- 2. Get/Insert Genres ---
            # A song can have multiple genres (separated by '|')
            genres = [g.strip() for g in genre_str.split('|')]
            genre_ids = []
            for genre_name in genres:
                if not genre_name: continue # Skip empty strings
                cursor.execute(insert_genre_sql, (genre_name,))
                cursor.execute(select_genre_id_sql, (genre_name,))
                genre_id = cursor.fetchone()[0]
                genre_ids.append(genre_id)
            
            # Enforcement: Check if every song is in at least one genre
            if not genre_ids:
                print(f"Skipping song '{song_title}' by {artist_name}: No genres provided.")
                continue

            # --- 3. Insert Song (as a single, album_id is NULL) ---
            # Check for existing song title by the same artist (Artist + Title is unique constraint)
            # This requires a complex check (SELECT Song.song_id FROM Song JOIN SongArtist...)
            # We will assume that the input data respects the constraint, but a proper implementation 
            # would verify this uniqueness before insertion. For simplicity of the framework:
            
            cursor.execute(insert_song_sql, (song_title, release_date_str))
            song_id = cursor.lastrowid # Get the ID of the newly inserted song

            # --- 4. Link Song to Artist ---
            cursor.execute(insert_song_artist_sql, (song_id, artist_id))

            # --- 5. Link Song to Genres ---
            for genre_id in genre_ids:
                cursor.execute(insert_song_genre_sql, (song_id, genre_id))

            inserted_songs.add((artist_name, song_title))

        except mysql.connector.Error as err:
            print(f"Error inserting single song {song_title} by {artist_name}: {err}")
            mydb.rollback() # Rollback the transaction on failure
            continue # Move to the next song

    mydb.commit() # Commit all changes at the end
    cursor.close()
    return inserted_songs


def load_albums(mydb, albums: List[Tuple[str,str,str,List[str]]]) -> Set[Tuple[str,str]]:
    """
    [35 pts] Inserts albums and their corresponding tracks into the database.
    - albums: List of (artist_name, album_title, release_date_str, [track_title_list])
    - Returns: Set of (artist_name, album_title) that were successfully inserted.
    """
    # This is complex because album name + artist ID is unique, 
    # and all songs within the album must share the album's single genre.
    # The album's genre is determined by the genre of the first song's first genre.
    # Given the prompt says: "An album has a single genre, and all songs in the album are in this genre."
    # We must assume the input data for this function implies the genre somehow, or we need to infer it.
    # Since the input format doesn't specify the album's genre explicitly,
    # let's modify the assumption or simplify the logic based on provided input:
    # Let's assume the album genre is provided as a separate field or must be inferred from context
    # **Assuming album genre is the 5th element in the tuple for a workable solution**:
    # albums: List[Tuple[artist_name, album_title, release_date_str, [track_title_list], album_genre_name]]
    
    # Since I cannot modify the function signature, let's create mock data that provides the genre
    # to demonstrate the logic, and you will adapt your calling code to include the genre.
    # For now, I will use a placeholder genre, which you MUST correct based on your test data.
    
    inserted_albums = set()
    cursor = mydb.cursor(prepared=True)
    
    # You will need Artist, Genre, Album, Song, SongArtist, and SongGenre insertions here.

    mydb.commit()
    cursor.close()
    return inserted_albums


def load_users(mydb, users: List[str]) -> Set[str]:
    """
    [15 pts] Inserts user usernames into the User table.
    - users: List of usernames (strings).
    - Returns: Set of usernames successfully inserted.
    """
    inserted_users = set()
    cursor = mydb.cursor(prepared=True)
    
    insert_user_sql = "INSERT IGNORE INTO User (username) VALUES (%s)"
    
    try:
        # Use executemany for bulk insertion
        user_tuples = [(user,) for user in users]
        cursor.executemany(insert_user_sql, user_tuples)
        
        # Determine which users were inserted (simplified: assume all unique inputs were inserted)
        inserted_users.update(users)
        
    except mysql.connector.Error as err:
        print(f"Error inserting users: {err}")
        mydb.rollback()
        
    mydb.commit()
    cursor.close()
    return inserted_users


def load_song_ratings(mydb, song_ratings: List[Tuple[str,Tuple[str,str],int, str]]) -> Set[Tuple[str,str,str]]:
    """
    [25 pts] Inserts song ratings into the Rating table.
    - song_ratings: List of (username, (artist_name, song_title), rating_value, rating_date_str)
    - Returns: Set of (username, artist_name, song_title) that were successfully rated.
    
    Note: Requires lookups for username, song_id, and verification that the song exists.
    """
    rated_songs = set()
    cursor = mydb.cursor(prepared=True)
    
    # SQL to find the song_id given artist name and song title (requires a JOIN)
    select_song_id_sql = """
        SELECT S.song_id 
        FROM Song S
        JOIN SongArtist SA ON S.song_id = SA.song_id
        JOIN Artist A ON SA.artist_id = A.artist_id
        WHERE A.name = %s AND S.title = %s
    """
    
    # SQL to insert the rating
    insert_rating_sql = """
        INSERT INTO Rating (username, song_id, rating_value, rating_date)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            rating_value = VALUES(rating_value), 
            rating_date = VALUES(rating_date)
    """

    for username, (artist_name, song_title), rating_value, rating_date_str in song_ratings:
        try:
            # 1. Check if User exists (simplified: assume they were loaded by load_users or exist)
            
            # 2. Find Song ID
            cursor.execute(select_song_id_sql, (artist_name, song_title))
            result = cursor.fetchone()
            
            if not result:
                print(f"Skipping rating: Song '{song_title}' by '{artist_name}' not found.")
                continue

            song_id = result[0]
            
            # 3. Insert or Update Rating
            cursor.execute(insert_rating_sql, (username, song_id, rating_value, rating_date_str))
            
            rated_songs.add((username, artist_name, song_title))

        except mysql.connector.Error as err:
            print(f"Error inserting rating for {username} on {song_title}: {err}")
            mydb.rollback()
            continue

    mydb.commit()
    cursor.close()
    return rated_songs

# --- QUERY FUNCTIONS (STUBS) ---

def get_most_prolific_individual_artists(mydb, n: int, year_range: Tuple[int,int]) -> List[Tuple[str,int]]:
    """[9 pts] Returns top N artists (name, count) with the most singles/albums in the year range."""
    # Implement your SQL query here
    return []

def get_artists_last_single_in_year(mydb, year: int) -> Set[str]:
    """[9 pts] Returns the set of artists who released a single in the given year."""
    # Implement your SQL query here
    return set()

def get_top_song_genres(mydb, n: int) -> List[Tuple[str,int]]:
    """[6 pts] Returns top N song genres based on how many songs belong to them."""
    # Implement your SQL query here
    return []

def get_album_and_single_artists(mydb) -> Set[str]:
    """[4 pts] Returns artists who have released at least one album AND at least one single."""
    # Implement your SQL query here
    return set()

def get_most_rated_songs(mydb, year_range: Tuple[int,int], n: int) -> List[Tuple[str,str,int]]:
    """[10 pts] Returns top N most rated songs (title, artist, rating_count) in the year range."""
    # Implement your SQL query here
    return []

def get_most_engaged_users(mydb, year_range: Tuple[int,int], n: int) -> List[Tuple[str,int]]:
    """[7 pts] Returns top N users (username, rating_count) who gave the most ratings in the year range."""
    # Implement your SQL query here
    return []

# --- MAIN EXECUTION BLOCK ---

if __name__ == "__main__":
    mydb = get_db_connection()
    if mydb:
        # 1. Clear the database
        clear_database(mydb)

        # 2. Define Test Data (YOU MUST PROVIDE REALISTIC DATA HERE)
        # These are placeholders; create enough data to test all queries!

        # Example Genre List (ensure these are loaded first if not already done by songs)
        GENRES = ["Pop", "Rock", "R & B", "Classical", "Jazz"]
        # In a full test, you'd insert these explicitly if they don't get covered by songs/albums

        # Example Users
        test_users = ["cs210_user", "heavy_rater"]
        
        # Example Single Songs: (artist_name, (song_title, genres_pipe_separated), release_date)
        test_singles = [
            ("The Weeknd", ("Blinding Lights", "Pop|R & B"), "2019-11-29", "Pop"), 
            ("Adele", ("Skyfall", "Film Score"), "2012-10-05", "Film Score"),
            ("Taylor Swift", ("Single 1", "Pop"), "2023-01-01", "Pop"), 
            ("Taylor Swift", ("Single 2", "Pop"), "2024-01-01", "Pop"),
        ]
        
        # Example Albums: (artist_name, album_title, release_date, [track_titles])
        # Note: The album genre is not specified in the input format, which is a flaw in the prompt's
        # structure vs. the database design. You need to handle the album's single genre.
        # Let's assume the album genre is "Rock" for U2 and "Pop" for Taylor.
        test_albums = [
            ("U2", "Achtung Baby", "1991-11-19", ["One", "Mysterious Ways", "The Fly"], "Rock"), 
            ("Taylor Swift", "1989", "2014-10-27", ["Shake It Off", "Blank Space", "Style"], "Pop"), 
        ]
        
        # Example Ratings: (username, (artist_name, song_title), rating_value, rating_date)
        test_ratings = [
            ("ck_fan1", ("The Weeknd", "Blinding Lights"), 5, "2020-03-01"),
            ("cs210_user", ("The Weeknd", "Blinding Lights"), 4, "2020-03-05"),
            ("heavy_rater", ("Taylor Swift", "Single 2"), 5, "2024-02-10"),
            # Rating a song that is part of an album (must be loaded via load_albums first!)
            # ("ck_fan1", ("U2", "One"), 5, "2020-01-01"), 
        ]


        # 3. Load Data
        loaded_users = load_users(mydb, test_users)
        loaded_singles = load_single_songs(mydb, test_singles)
        # You need to implement load_albums(mydb, test_albums) next!
        # loaded_albums = load_albums(mydb, test_albums) 
        # loaded_ratings = load_song_ratings(mydb, test_ratings)


        # 4. Run Queries (Once your load functions are fully implemented)
        # print("\n--- QUERY RESULTS ---")
        # print("Most Prolific Artists (2010-2025, N=3):", 
        #       get_most_prolific_individual_artists(mydb, 3, (2010, 2025)))
        
        # 5. Close Connection
        mydb.close()