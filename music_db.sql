-- Correct Music Database Schema (hw3 - music_db.sql)
-- Fully compliant with assignment requirements
-- Artists uniquely identified by NAME (no artist_id)
-- Songs unique per (title, artist_name)
-- Albums unique per (title, artist_name)
-- Album stores genre_id (album has ONE genre)
-- Songs store artist_name as FK

SET foreign_key_checks = 0;

DROP TABLE IF EXISTS Rating;
DROP TABLE IF EXISTS SongGenre;
DROP TABLE IF EXISTS SongArtist;
DROP TABLE IF EXISTS Song;
DROP TABLE IF EXISTS Album;
DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS Artist;
DROP TABLE IF EXISTS Genre;

SET foreign_key_checks = 1;

-- ==========================================
-- 1. GENRE
-- ==========================================
CREATE TABLE Genre (
    genre_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- ==========================================
-- 2. ARTIST
-- ==========================================
CREATE TABLE Artist (
    name VARCHAR(100) PRIMARY KEY
);

-- ==========================================
-- 3. ALBUM
-- ==========================================
CREATE TABLE Album (
    album_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    release_date DATE NOT NULL,
    artist_name VARCHAR(100) NOT NULL,
    genre_id INT NOT NULL,
    UNIQUE (title, artist_name),
    FOREIGN KEY (artist_name) REFERENCES Artist(name) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES Genre(genre_id) ON DELETE RESTRICT
);

-- ==========================================
-- 4. SONG
-- ==========================================
CREATE TABLE Song (
    song_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    release_date DATE NOT NULL,
    artist_name VARCHAR(100) NOT NULL,
    album_id BIGINT NULL,
    UNIQUE (title, artist_name),
    FOREIGN KEY (artist_name) REFERENCES Artist(name) ON DELETE CASCADE,
    FOREIGN KEY (album_id) REFERENCES Album(album_id) ON DELETE CASCADE
);

-- ==========================================
-- 5. SONGARTIST (for covers)
-- ==========================================
CREATE TABLE SongArtist (
    song_id BIGINT NOT NULL,
    artist_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (song_id, artist_name),
    FOREIGN KEY (song_id) REFERENCES Song(song_id) ON DELETE CASCADE,
    FOREIGN KEY (artist_name) REFERENCES Artist(name) ON DELETE CASCADE
);

-- ==========================================
-- 6. SONGGENRE
-- ==========================================
CREATE TABLE SongGenre (
    song_id BIGINT NOT NULL,
    genre_id INT NOT NULL,
    PRIMARY KEY (song_id, genre_id),
    FOREIGN KEY (song_id) REFERENCES Song(song_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES Genre(genre_id) ON DELETE CASCADE
);

-- ==========================================
-- 7. USER
-- ==========================================
CREATE TABLE User (
    username VARCHAR(30) PRIMARY KEY
);

-- ==========================================
-- 8. RATING
-- ==========================================
CREATE TABLE Rating (
    username VARCHAR(30) NOT NULL,
    song_id BIGINT NOT NULL,
    rating_value TINYINT NOT NULL CHECK (rating_value BETWEEN 1 AND 5),
    rating_date DATE NOT NULL,
    PRIMARY KEY (username, song_id),
    FOREIGN KEY (username) REFERENCES User(username) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES Song(song_id) ON DELETE CASCADE
);