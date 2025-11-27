from typing import Tuple, List, Set

def clear_database(mydb):
    """
    Deletes all rows from all tables of the database.
    Order matters because of foreign key constraints.
    """
    cursor = mydb.cursor()

    # Order: children → parents
    tables = [
        "Rating",
        "SongGenre",
        "SongArtist",
        "Song",
        "Album",
        "User",
        "Artist",
        "Genre"
    ]

    for table in tables:
        cursor.execute(f"DELETE FROM {table}")

    mydb.commit()


def load_single_songs(mydb, single_songs):
    """
    Inserts single songs into the database.
    Returns set of (song, artist) that were rejected.
    """
    cursor = mydb.cursor()
    rejects = set()

    for title, genres, artist, release_date in single_songs:

        # 1. Ensure artist exists
        cursor.execute("INSERT IGNORE INTO Artist(name) VALUES (%s)", (artist,))

        # 2. Ensure each genre exists
        for g in genres:
            cursor.execute("INSERT IGNORE INTO Genre(name) VALUES (%s)", (g,))

        # 3. Try to insert song (as a single → album_id = NULL)
        try:
            cursor.execute("""
                INSERT INTO Song (title, release_date, artist_name, album_id)
                VALUES (%s, %s, %s, NULL)
            """, (title, release_date, artist))
        except:
            # Already exists → reject
            rejects.add((title, artist))
            continue

        # 4. Get song_id to insert genres
        cursor.execute("""
            SELECT song_id FROM Song 
            WHERE title=%s AND artist_name=%s
        """, (title, artist))
        song_id = cursor.fetchone()[0]

        # 5. Link genres
        for g in genres:
            cursor.execute("SELECT genre_id FROM Genre WHERE name=%s", (g,))
            gid = cursor.fetchone()[0]

            cursor.execute("""
                INSERT IGNORE INTO SongGenre(song_id, genre_id)
                VALUES (%s, %s)
            """, (song_id, gid))

    mydb.commit()
    return rejects


def get_most_prolific_individual_artists(mydb, n, year_range):
    """
    Returns the top n artists with the most single releases in a given year range.
    """
    cursor = mydb.cursor()
    start_year, end_year = year_range

    cursor.execute("""
        SELECT artist_name, COUNT(*) AS num_singles
        FROM Song
        WHERE album_id IS NULL
          AND YEAR(release_date) BETWEEN %s AND %s
        GROUP BY artist_name
        ORDER BY num_singles DESC, artist_name ASC
        LIMIT %s;
    """, (start_year, end_year, n))

    return cursor.fetchall()


def get_artists_last_single_in_year(mydb, year: int) -> Set[str]:
    """
    Get all artists who released their last single in the given year.
    """
    pass
    

def load_albums(mydb, albums: List[Tuple[str, str, str, List[str]]]) -> Set[Tuple[str, str]]:
    """
    Add albums to the database.
    """
    pass


def get_top_song_genres(mydb, n: int) -> List[Tuple[str, int]]:
    """
    Get n genres that are most represented in number of songs.
    """
    pass


def get_album_and_single_artists(mydb) -> Set[str]:
    """
    Get artists who have released albums as well as singles.
    """
    pass


def load_users(mydb, users: List[str]) -> Set[str]:
    """
    Add users to the database. 
    """
    pass


def load_song_ratings(mydb, song_ratings: List[Tuple[str, Tuple[str, str], int, str]]) -> Set[Tuple[str, str, str]]:
    """
    Load ratings for songs.
    """
    pass


def get_most_rated_songs(mydb, year_range: Tuple[int, int], n: int) -> List[Tuple[str, str, int]]:
    """
    Get the top n most rated songs in the year range.
    """
    pass


def get_most_engaged_users(mydb, year_range: Tuple[int, int], n: int) -> List[Tuple[str, int]]:
    """
    Get the top n most engaged users by number of songs rated.
    """
    pass


def main():
    pass


if __name__ == "__main__":
    main()