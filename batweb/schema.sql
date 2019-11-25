DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS bat;
DROP TABLE IF EXISTS terminal;
DROP TABLE IF EXISTS detection;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mail TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL
);
CREATE TABLE bat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT UNIQUE NOT NULL,
    scientificname TEXT NOT NULL,
    description TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id)
);
CREATE TABLE terminal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT UNIQUE NOT NULL,
    location TEXT NOT NULL,
    information TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE detection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bat_id INTEGER NOT NULL,
    terminal_id INTEGER NOT NULL,
    detected TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    information TEXT NOT NULL,
    FOREIGN KEY (bat_id) REFERENCES bat (id),
    FOREIGN KEY (terminal_id) REFERENCES terminal (id)
);