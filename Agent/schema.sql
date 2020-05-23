DROP DATABASE IF EXISTS {database};
CREATE DATABASE {database};
USE {database};
CREATE TABLE loc
(
    id  SERIAL PRIMARY KEY,
    dir VARCHAR(255) DEFAULT './' UNIQUE NOT NULL
);
CREATE TABLE user
(
    username VARCHAR(255) UNIQUE PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    dir_id   BIGINT(20)   NOT NULL,
    FOREIGN KEY (dir_id) REFERENCES loc (dir)
);
INSERT INTO loc(dir)
VALUES ("Agent/faces/");