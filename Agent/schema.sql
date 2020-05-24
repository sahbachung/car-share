DROP DATABASE IF EXISTS {database};
CREATE DATABASE {database};
USE {database};
CREATE TABLE user
(
    username VARCHAR(255) UNIQUE PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    dir VARCHAR(255) NOT NULL
);