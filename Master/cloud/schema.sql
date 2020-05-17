DROP TABLE user;
CREATE TABLE user(
	id SERIAL PRIMARY KEY,
	username VARCHAR(255) UNIQUE NOT NULL,
	password VARCHAR(255) NOT NULL,
	firstname VARCHAR(255),
	lastname VARCHAR(255),
	email VARCHAR(255)
);