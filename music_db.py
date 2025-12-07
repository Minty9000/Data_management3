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
        except Exception:
            # Already exists (because of UNIQUE(title, artist_name)) → reject
            rejects.add((title, artist))
            continue

        # 4. Get song_id to insert genres and SongArtist
        cursor.execute("""
            SELECT song_id FROM Song 
            WHERE title=%s AND artist_name=%s
        """, (title, artist))
        row = cursor.fetchone()
        if not row:
            # Shouldn't happen, but be defensive
            continue
        song_id = row[0]

        # 5. Link genres
        for g in genres:
            cursor.execute("SELECT genre_id FROM Genre WHERE name=%s", (g,))
            gid_row = cursor.fetchone()
            if not gid_row:
                continue
            gid = gid_row[0]

            cursor.execute("""
                INSERT IGNORE INTO SongGenre(song_id, genre_id)
                VALUES (%s, %s)
            """, (song_id, gid))

        # 6. Link artist to song in SongArtist table
        cursor.execute("""
            INSERT IGNORE INTO SongArtist(song_id, artist_name)
            VALUES (%s, %s)
        """, (song_id, artist))

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

    "Last single" means: take all singles (Song with album_id IS NULL),
    find the maximum YEAR(release_date) for each artist, and keep those
    whose max year equals the input year.
    """
    cursor = mydb.cursor()

    cursor.execute("""
        SELECT artist_name
        FROM Song
        WHERE album_id IS NULL
        GROUP BY artist_name
        HAVING MAX(YEAR(release_date)) = %s
    """, (year,))

    return {row[0] for row in cursor.fetchall()}


def load_albums(mydb, albums: List[Tuple[str, str, str, str, List[str]]]) -> Set[Tuple[str, str]]:
    """
    Add albums to the database.

    albums: list of tuples (album_title, genre_name, artist_name, release_date, [song_titles])

    Returns:
        Set of (album_title, artist_name) that were rejected because
        the artist already has an album with that title.
    """
    cursor = mydb.cursor()
    rejects: Set[Tuple[str, str]] = set()

    for album_title, genre_name, artist_name, release_date, song_titles in albums:
        # ensure artist exists
        cursor.execute("INSERT IGNORE INTO Artist(name) VALUES (%s)", (artist_name,))

        # ensure genre exists
        cursor.execute("INSERT IGNORE INTO Genre(name) VALUES (%s)", (genre_name,))
        cursor.execute("SELECT genre_id FROM Genre WHERE name=%s", (genre_name,))
        genre_row = cursor.fetchone()
        if not genre_row:
            rejects.add((album_title, artist_name))
            continue
        genre_id = genre_row[0]

        # check if this (album_title, artist_name) already exists
        cursor.execute("""
            SELECT album_id
            FROM Album
            WHERE title = %s AND artist_name = %s
        """, (album_title, artist_name))
        if cursor.fetchone():
            # reject, don't insert songs for this album
            rejects.add((album_title, artist_name))
            continue

        # insert album
        cursor.execute("""
            INSERT INTO Album (title, release_date, artist_name, genre_id)
            VALUES (%s, %s, %s, %s)
        """, (album_title, release_date, artist_name, genre_id))
        album_id = cursor.lastrowid

        # insert songs that belong to this album
        for song_title in song_titles:
            # try to insert song; uniqueness is (title, artist_name)
            try:
                cursor.execute("""
                    INSERT INTO Song (title, release_date, artist_name, album_id)
                    VALUES (%s, %s, %s, %s)
                """, (song_title, release_date, artist_name, album_id))
            except Exception:
                # conflict on (title, artist_name) → skip this song
                continue

            # get song_id
            cursor.execute("""
                SELECT song_id FROM Song
                WHERE title=%s AND artist_name=%s
                  AND album_id = %s
            """, (song_title, artist_name, album_id))
            row = cursor.fetchone()
            if not row:
                continue
            song_id = row[0]

            # link album genre to song
            cursor.execute("""
                INSERT IGNORE INTO SongGenre(song_id, genre_id)
                VALUES (%s, %s)
            """, (song_id, genre_id))

            # link artist to song in SongArtist table
            cursor.execute("""
                INSERT IGNORE INTO SongArtist(song_id, artist_name)
                VALUES (%s, %s)
            """, (song_id, artist_name))

    mydb.commit()
    return rejects


def get_top_song_genres(mydb, n: int) -> List[Tuple[str, int]]:
    """
    Get n genres that are most represented in number of songs.
    Songs include singles as well as songs in albums.

    Returns:
        list of (genre_name, number_of_songs), sorted by:
        - descending number_of_songs
        - then alphabetical genre_name
    """
    cursor = mydb.cursor()

    cursor.execute("""
        SELECT g.name, COUNT(*) AS num_songs
        FROM SongGenre sg
        JOIN Genre g ON sg.genre_id = g.genre_id
        GROUP BY g.genre_id, g.name
        ORDER BY num_songs DESC, g.name ASC
        LIMIT %s
    """, (n,))

    return cursor.fetchall()


def get_album_and_single_artists(mydb) -> Set[str]:
    """
    Get artists who have released albums as well as singles.

    - Album artist: appears in Album.artist_name
    - Single artist: appears in Song.artist_name for rows with album_id IS NULL
    """
    cursor = mydb.cursor()

    cursor.execute("""
        SELECT DISTINCT s.artist_name
        FROM Song s
        JOIN Album a ON s.artist_name = a.artist_name
        WHERE s.album_id IS NULL
    """)

    return {row[0] for row in cursor.fetchall()}


def load_users(mydb, users: List[str]) -> Set[str]:
    """
    Add users to the database.

    Returns:
        Set of usernames that were NOT added (rejected)
        because they already exist.
    """
    cursor = mydb.cursor()
    rejects: Set[str] = set()

    for username in users:
        # try to insert, but ignore on duplicate
        cursor.execute("INSERT IGNORE INTO User(username) VALUES (%s)", (username,))
        # if rowcount == 0, insert failed (duplicate)
        if cursor.rowcount == 0:
            rejects.add(username)

    mydb.commit()
    return rejects


def load_song_ratings(
    mydb,
    song_ratings: List[Tuple[str, Tuple[str, str], int, str]]
) -> Set[Tuple[str, str, str]]:
    """
    Load ratings for songs.

    song_ratings: list of (username, (artist_name, song_title), rating, date)

    Returns:
        set of (username, artist_name, song_title) that are rejected because:
          (a) username not in User
          (b) (artist,song) not in Song
          (c) user already rated that song
          (d) rating not in 1..5
    """
    cursor = mydb.cursor()
    rejects: Set[Tuple[str, str, str]] = set()

    for username, (artist_name, song_title), rating_value, rating_date in song_ratings:
        # (d) rating out of range
        if rating_value < 1 or rating_value > 5:
            rejects.add((username, artist_name, song_title))
            continue

        # (a) check user exists
        cursor.execute("SELECT 1 FROM User WHERE username=%s", (username,))
        if cursor.fetchone() is None:
            rejects.add((username, artist_name, song_title))
            continue

        # (b) find song by (artist_name, title)
        cursor.execute("""
            SELECT song_id
            FROM Song
            WHERE title = %s AND artist_name = %s
        """, (song_title, artist_name))
        song_row = cursor.fetchone()
        if song_row is None:
            rejects.add((username, artist_name, song_title))
            continue
        song_id = song_row[0]

        # (c) check if this (username, song_id) already rated
        cursor.execute("""
            SELECT 1
            FROM Rating
            WHERE username=%s AND song_id=%s
        """, (username, song_id))
        if cursor.fetchone() is not None:
            rejects.add((username, artist_name, song_title))
            continue

        # all good, insert rating
        cursor.execute("""
            INSERT INTO Rating (username, song_id, rating_value, rating_date)
            VALUES (%s, %s, %s, %s)
        """, (username, song_id, rating_value, rating_date))

    mydb.commit()
    return rejects


def get_most_rated_songs(
    mydb,
    year_range: Tuple[int, int],
    n: int
) -> List[Tuple[str, str, int]]:
    """
    Get the top n most rated songs in the given year range (inclusive).

    "Most rated" = number of ratings (count of Rating rows),
    not the rating score.
    Ties broken by alphabetical order of song title.
    """
    cursor = mydb.cursor()
    start_year, end_year = year_range

    cursor.execute("""
        SELECT s.title, s.artist_name, COUNT(*) AS num_ratings
        FROM Rating r
        JOIN Song s ON r.song_id = s.song_id
        WHERE YEAR(r.rating_date) BETWEEN %s AND %s
        GROUP BY r.song_id, s.title, s.artist_name
        ORDER BY num_ratings DESC, s.title ASC
        LIMIT %s
    """, (start_year, end_year, n))

    return cursor.fetchall()


def get_most_engaged_users(
    mydb,
    year_range: Tuple[int, int],
    n: int
) -> List[Tuple[str, int]]:
    """
    Get the top n most engaged users by number of songs they have rated
    in the given year range.

    Ties broken by alphabetical username.
    """
    cursor = mydb.cursor()
    start_year, end_year = year_range

    cursor.execute("""
        SELECT r.username, COUNT(*) AS num_rated
        FROM Rating r
        WHERE YEAR(r.rating_date) BETWEEN %s AND %s
        GROUP BY r.username
        ORDER BY num_rated DESC, r.username ASC
        LIMIT %s
    """, (start_year, end_year, n))

    return cursor.fetchall()


def main():
    # not required by the assignment; typically left empty or used
    # for ad-hoc testing.
    pass


if __name__ == "__main__":
    main()