DROP TABLE IF EXISTS booking;
DROP TABLE IF EXISTS car;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS make;
DROP TABLE IF EXISTS model;
DROP TABLE IF EXISTS location;
CREATE TABLE user (
	id SERIAL PRIMARY KEY,
	username VARCHAR(255) UNIQUE NOT NULL,
	password VARCHAR(255) NOT NULL,
	firstname VARCHAR(255),
	lastname VARCHAR(255),
	email VARCHAR(255),
	lastlogin DATE
);
CREATE TABLE make (
	id SERIAL PRIMARY KEY,
	make VARCHAR(255)
);
CREATE TABLE model (
	id SERIAL PRIMARY KEY,
	model VARCHAR(255)
);
CREATE TABLE location (
	id SERIAL PRIMARY KEY,
	name VARCHAR(255)
);
CREATE TABLE car (
	id SERIAL PRIMARY KEY,
	registration VARCHAR(255) NOT NULL,
	make_id BIGINT(20) UNSIGNED NOT NULL,
	model_id BIGINT(20) UNSIGNED NOT NULL,
	colour VARCHAR(16),
	seats INTEGER(2) NOT NULL,
	location_id BIGINT(20) UNSIGNED NOT NULL,
	FOREIGN KEY (make_id) REFERENCES make (id),
	FOREIGN KEY (model_id) REFERENCES model (id),
	FOREIGN KEY (location_id) REFERENCES location (id)
);
CREATE TABLE booking (
	user_id BIGINT(20) UNSIGNED NOT NULL,
	car_id BIGINT(20) UNSIGNED NOT NULL,
	booked DATE NOT NULL,
	duration INTEGER(3) NOT NULL,
	returned DATE DEFAULT NULL,
	FOREIGN KEY (user_id) REFERENCES user (id),
	FOREIGN KEY (car_id) REFERENCES car (id)
);