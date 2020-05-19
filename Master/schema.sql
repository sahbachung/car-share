DROP TABLE IF EXISTS booking;
DROP TABLE IF EXISTS car;
DROP TABLE IF EXISTS role;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS make;
DROP TABLE IF EXISTS model;
DROP TABLE IF EXISTS location;
CREATE TABLE role(
	id INTEGER PRIMARY KEY,
	role VARCHAR(15) NOT NULL,
);
CREATE TABLE user(
	id SERIAL PRIMARY KEY,
	username VARCHAR(255) UNIQUE NOT NULL,
	password VARCHAR(255) NOT NULL,
	role_id INTEGER DEFAULT 0,
	firstname VARCHAR(255),
	lastname VARCHAR(255),
	email VARCHAR(255) UNIQUE NOT NULL,
	lastlogin DATE,
	FOREIGN KEY (role_id) REFERENCES role (id)
);
CREATE TABLE make(
	id SERIAL PRIMARY KEY,
	make VARCHAR(255)
);
CREATE TABLE model(
	id SERIAL PRIMARY KEY,
	model VARCHAR(255)
);
CREATE TABLE location(
	id SERIAL PRIMARY KEY,
	name VARCHAR(255)
);
CREATE TABLE car(
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
CREATE TABLE booking(
	event_id SERIAL PRIMARY KEY,
	user_id BIGINT(20) UNSIGNED NOT NULL,
	car_id BIGINT(20) UNSIGNED NOT NULL,
	booked DATE NOT NULL,
	duration INTEGER(3) NOT NULL,
	returned DATE DEFAULT NULL,
	FOREIGN KEY (user_id) REFERENCES user (id),
	FOREIGN KEY (car_id) REFERENCES car (id)
);
INSERT INTO role(id, role) VALUES(0, 'user');
INSERT INTO role(id, role) VALUES(1, 'admin');
INSERT INTO user(username, password, email) VALUES('root', '784a9df876e9cf7a4d78a7abf6bcea92863c7f5d', 'car-share@pro-flux-277109.iam.gserviceaccount.com');