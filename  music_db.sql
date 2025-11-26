--
-- Music Database Schema (hw3 - music_db.sql)
--
-- This script contains the CREATE TABLE statements for the Music Database,
-- based on the provided entity description and schema design.
--
-- Data types and sizes are chosen to be minimally large yet realistic for a
-- large-scale music service.
--

-- Set up the environment
SET foreign_key_checks = 0; -- Temporarily disable checks for dropping/creating tables

--
-- Table Drop Statements: Drop tables in reverse dependency order
--
DROP TABLE IF EXISTS Rating;
DROP TABLE IF EXISTS SongGenre;
DROP TABLE IF EXISTS SongArtist;
DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS Song;
DROP TABLE IF EXISTS Album;
DROP TABLE IF EXISTS Artist;
DROP TABLE IF EXISTS Genre;

--
-- 1. Genre Table
-- Stores predefined genres.
--
CREATE TABLE Genre (
    genre_id INT AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE, -- Genre names are unique and relatively short
    PRIMARY KEY (genre_id)
);

--
-- 2. Artist Table
-- Stores individual artists or bands. Uniquely identified by a system-generated ID.
-- The name itself must be unique.
--
CREATE TABLE Artist (
    artist_id BIGINT AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE, -- Artist name can be long (e.g., band name)
    PRIMARY KEY (artist_id)
);

--
-- 3. Album Table
-- Stores albums, which are collections of songs by an artist.
-- The combination of title and artist_id must be unique.
--
CREATE TABLE Album (
    album_id BIGINT AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    release_date DATE NOT NULL,
    artist_id BIGINT NOT NULL,
    -- Albums have a single genre, which applies to all songs within it.
    -- Storing it here minimizes redundancy with the SongGenre table for album songs.
    genre_id INT NOT NULL,
    PRIMARY KEY (album_id),
    UNIQUE KEY uk_album_artist (title, artist_id), -- Album name + Artist must be unique
    FOREIGN KEY (artist_id) REFERENCES Artist(artist_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES Genre(genre_id) ON DELETE RESTRICT
);

--
-- 4. Song Table
-- Stores song metadata.
-- album_id is NULL for single songs, NOT NULL for album tracks.
-- release_date for album tracks is the album's release date, and for singles it's the single's date.
-- A song is uniquely identified by its ID. The combination of title and artist is handled by SongArtist table.
--
CREATE TABLE Song (
    song_id BIGINT AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    release_date DATE NOT NULL,
    album_id BIGINT NULL, -- NULL indicates a single, NOT NULL indicates an album track
    PRIMARY KEY (song_id),
    FOREIGN KEY (album_id) REFERENCES Album(album_id) ON DELETE CASCADE
);

--
-- 5. SongArtist Table (Junction Table)
-- Handles the relationship between Song and Artist (a song is performed by one artist).
-- The unique constraint enforces the rule: "An artist may not record the same song (title) more than once"
-- by combining (artist_id, song title from Song). This is handled in the Python layer
-- during insertion/lookup, but we enforce the primary relationship here.
-- Note: We rely on the python logic for the 'title' uniqueness across an artist's discography.
-- The primary key ensures a song is only associated once with a given artist.
--
CREATE TABLE SongArtist (
    song_id BIGINT,
    artist_id BIGINT,
    PRIMARY KEY (song_id, artist_id),
    FOREIGN KEY (song_id) REFERENCES Song(song_id) ON DELETE CASCADE,
    FOREIGN KEY (artist_id) REFERENCES Artist(artist_id) ON DELETE CASCADE
);

--
-- 6. SongGenre Table (Junction Table)
-- Handles the many-to-many relationship between Song and Genre (A song belongs to one or more genres).
--
CREATE TABLE SongGenre (
    song_id BIGINT,
    genre_id INT,
    PRIMARY KEY (song_id, genre_id),
    FOREIGN KEY (song_id) REFERENCES Song(song_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES Genre(genre_id) ON DELETE CASCADE
);

--
-- 7. User Table
-- Stores user data. Uniquely identified by their username.
--
CREATE TABLE User (
    username VARCHAR(30), -- Assumed length for a realistic username (e.g., Spotify, Amazon)
    PRIMARY KEY (username)
);

--
-- 8. Rating Table
-- Stores song ratings given by users.
-- The combination of username and song_id is the primary key (a user can rate a song only once).
--
CREATE TABLE Rating (
    username VARCHAR(30),
    song_id BIGINT,
    rating_value TINYINT NOT NULL CHECK (rating_value BETWEEN 1 AND 5), -- Rating is limited to 1,2,3,4, or 5
    rating_date DATE NOT NULL,
    PRIMARY KEY (username, song_id), -- A user can only rate a specific song once
    FOREIGN KEY (username) REFERENCES User(username) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES Song(song_id) ON DELETE CASCADE
);

-- Re-enable foreign key checks
SET foreign_key_checks = 1;