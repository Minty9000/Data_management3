CREATE TABLE Artist (
    name VARCHAR(100) PRIMARY KEY
);

CREATE TABLE Genre (
    genre_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) UNIQUE
);

CREATE TABLE Album (
    album_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    release_date DATE,
    artist_name VARCHAR(100),
    genre_id INT NOT NULL,
    UNIQUE (title, artist_name),
    FOREIGN KEY (artist_name) REFERENCES Artist(name),
    FOREIGN KEY (genre_id) REFERENCES Genre(genre_id)
);

CREATE TABLE Song (
    song_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    release_date DATE,
    artist_name VARCHAR(100),
    album_id BIGINT,
    UNIQUE (title, artist_name),
    FOREIGN KEY (artist_name) REFERENCES Artist(name),
    FOREIGN KEY (album_id) REFERENCES Album(album_id)
);

CREATE TABLE SongGenre (
    song_id BIGINT,
    genre_id INT,
    PRIMARY KEY (song_id, genre_id),
    FOREIGN KEY (song_id) REFERENCES Song(song_id),
    FOREIGN KEY (genre_id) REFERENCES Genre(genre_id)
);

CREATE TABLE SongArtist (
    song_id BIGINT,
    artist_name VARCHAR(100),
    PRIMARY KEY (song_id, artist_name),
    FOREIGN KEY (song_id) REFERENCES Song(song_id),
    FOREIGN KEY (artist_name) REFERENCES Artist(name)
);

CREATE TABLE User (
    username VARCHAR(30) PRIMARY KEY
);

CREATE TABLE Rating (
    username VARCHAR(30),
    song_id BIGINT,
    rating_value TINYINT,
    rating_date DATE,
    PRIMARY KEY (username, song_id),
    FOREIGN KEY (username) REFERENCES User(username),
    FOREIGN KEY (song_id) REFERENCES Song(song_id)
);