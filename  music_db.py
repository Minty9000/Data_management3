from typing import Tuple, List, Set

def clear_database(mydb):
    """
    Deletes all the rows from all the tables of the database.
    """
    
    pass


def load_single_songs(mydb, single_songs: List[Tuple[str, Tuple[str, ...], str, str]]) -> Set[Tuple[str, str]]:
    """
    Add single songs to the database. 
    """
    pass


def get_most_prolific_individual_artists(mydb, n: int, year_range: Tuple[int, int]) -> List[Tuple[str, int]]:   
    """
    Get the top n most prolific individual artists by number of singles released.
    """
    pass


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