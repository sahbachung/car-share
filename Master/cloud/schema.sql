DROP TABLE user, car, car_types CASCADE;
CREATE TABLE user (
	id SERIAL PRIMARY KEY,
	username VARCHAR(255) UNIQUE NOT NULL,
	password VARCHAR(255) NOT NULL,
	firstname VARCHAR(255),
	lastname VARCHAR(255),
	email VARCHAR(255)
);
CREATE TABLE car (
	id SERIAL PRIMARY KEY,
	registration VARCHAR(255) NOT NULL,
	make BIGINT(20),
	model BIGINT(20),
	colour VARCHAR(16),
	seats INTEGER(2),
	location BIGINT(20),
	FOREIGN KEY (make) REFERENCES make(id),
	FOREIGN KEY (model) REFERENCES model(id),
	FOREIGN KEY (location) REFERENCES location(id)
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
CREATE TABLE booking (
	user_id BIGINT(20) PRIMARY KEY,
	car_id BIGINT(20) PRIMARY KEY,
	booked DATE NOT NULL,
	duration INTEGER(3) NOT NULL,
	returned DATE DEFAULT NULL,
	FOREIGN KEY (user_id) REFERENCES user(id),
	FOREIGN KEY (car_id) REFERENCES car(id)
);