from mysql.connector import MySQLConnection
from mysql.connector.errors import ProgrammingError

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from oauth2client.service_account import ServiceAccountCredentials

import pickle
import os.path
import re
import argparse
import string
from datetime import datetime, timedelta

class Controller(MySQLConnection):

	def __init__(self, **kwargs):
		super().__init__(
			host 		= kwargs.get("host"),
			port 		= kwargs.get("port"),
			user 		= kwargs.get("user"), 
			password 	= kwargs.get("password"))
		self.autocommit = True
		self.cu = self.cursor()
		self.cal = Calendar(self)
		if kwargs.get("db"):
			self.use(kwargs.get("db"))

	def __enter__(self):
		autocommit = False
		return self

	def __exit__(self, type, value, tb):
		self.cu.execute("COMMIT;")
		self.autocommit = True

	def use(self, db):
		try:
			self.cu.execute("USE %s" % db)
		except ProgrammingError:
			self.cu.execute("CREATE DATABASE %s" % db)
			self.use(db)


	def init_database(self, schema_loc):
		for q in QueryBuilder.load_commands(schema_loc):
			self.cu.execute(q)

	def query_username(self, username) -> bool:
		self.cu.execute(QueryBuilder.find_user(username))
		return bool(self.cu.fetchall())

	def verify_hash(self, username, key_hash) -> bool:
		self.cu.execute(QueryBuilder.retrieve_hash(username))
		q = self.cu.fetchall()[0]
		return bool(q) and q[0]==key_hash

	def login(self, username, password) -> bool:
		if not self.query_username(username) or not self.verify_hash(username, password):
			return False
		else:
			self.cu.execute(QueryBuilder.update_lastlogin(username))

	def register_user(self, username, password, first="", last="", email="") -> bool:
		print("register " + username)
		if not first: first = "NULL"
		if not last: last = "NULL"
		if not email: email = "NULL"
		if self.query_username(username):
			return False
		self.cu.execute(QueryBuilder.add_user(username, password, first, last, email))
		return True

	def book_car(self, event_id, username, car_id, date, duration):
		# YYYYMMDD HH:MM:SS [AP]M
		Controller._parse_date(date)
		assert self.car_is_free(car_id)
		assert duration > 0
		q = QueryBuilder.make_booking(
			event_id=event_id, 
			user_id=self.get_user_details(username)[0],
			car_id=car_id, booked=date)

	@staticmethod
	def _parse_date(d) -> (int, int, int, int, int, int):
		assert re.search("[0-9]{8} [0-9]{2}:[0-9]{2}:[0-9]{2} [AP]M", d)
		year = int(d[0:4])
		month = int(d[4:6])
		day = int(d[6:8])
		hour = int(d[9:11])
		minute = int(d[12:14])
		second = int(d[15:17])
		if d[-2]=="P": hour = (hour + 12) % 24
		return year, month, day, hour, minute, second


	def get_all_cars(self) -> tuple:
		self.cu.execute(QueryBuilder.search_car([]))
		return self.cu.fetchall()

	def search_cars(self, display_fields=list(), **kwargs):
		self.cu.execute(QueryBuilder.search_car(display_fields, **kwargs))
		return self.cu.fetchall()

	def get_history(self, username) -> list:
		self.cu.execute(QueryBuilder.get_history(username))
		return self.cu.fetchall()

	def get_user_details(self, username) -> tuple:
		self.cu.execute(QueryBuilder.get_user_info(username))
		return self.cu.fetchall()[0]

	def get_next_event_id(self) -> int:
		self.cu.execute("SELECT MAX(event_id) FROM booking;")
		eid = self.cu.fetchall()
		if not eid:
			return 0
		else:
			return int(eid[0][0]) + 1

	def get_email(self, user) -> str:
		self.cu.execute("SELECT email FROM user WHERE username LIKE '{0}'".format(user))
		r = self.cu.fetchall()
		if not r:
			raise ValueNotFound
		else:
			return r[0][0]

	def get_car(self, car_id) -> bool:
		self.cu.execute(QueryBuilder.get_car(car_id))
		return bool(self.cu.fetchall())

	def car_is_free(self, car_id) -> bool:
		if not self.get_car(car_id):
			return False
		self.cu.execute(QueryBuilder.check_car_free(car_id))
		return not bool(self.cu.fetchall())


class Calendar:
	SCOPES = ['https://www.googleapis.com/auth/calendar']
	creds = None
	pkl = "Master/token.pickle"
	credentials = "Master/credentials.json"

	def __init__(self, controller: Controller):
		self.controller = controller
		self.service = self.get_service()

	def get_service(self):
		if os.path.exists(self.pkl):
			with open(self.pkl, "rb") as token:
				self.creds = pickle.load(token)
		if not self.creds:
			if self.creds and self.creds.expired and self.creds.refresh_token:
				self.creds.refresh(Request())
			else:
				self.creds = ServiceAccountCredentials.from_json_keyfile_name(
        			filename=self.credentials,
        			scopes=self.SCOPES)
			with open(self.pkl, "wb") as token:
				pickle.dump(self.creds, token)
		return build("calendar", "v3", credentials=self.creds)

	def add_event(self, user, car_id, date, duration) -> bool:
		user_info = self.controller.get_user_details(user)
		events = self.service.events()
		event_id = self.controller.get_next_event_id()
		email = self.get_email(user)
		start, end = self._parse_dates(date, duration)
		event = {
			  'summary': 'Car booking',
			  'start': {
			    'dateTime': start,
			    'timeZone': 'America/Los_Angeles'
			  },
			  'end': {
			    'dateTime': end,
			    'timeZone': 'Australia/Melbourne'
			  },
			  'attendees': [
			    {
			      'email': email,
			    },
			  ],
			}
		events.insert(calendarId="primary", body=event).execute()
		self.controller.book_car(eventId, user, car_id, date, duration)
		return True
		
		def _parse_date(self, d) -> str:
			assert re.search("[0-9]{8} [0-9]{2}:[0-9]{2}:[0-9]{2} [AP]M", d)
			year = int(d[0:4])
			month = int(d[4:6])
			day = int(d[6:8])
			hour = int(d[9:11])
			minute = int(d[12:14])
			second = int(d[15:17])
			if d[-2]=="P": hour = (hour + 12) % 24
			return "{year}-{month}-{day}T{hour}:{minute}:{second}".format(
					year=year,
					month=month,
					day=day,
					hour=hour,
					minute=minute,
					second=second)

		def _parse_dates(self, date, duration) -> (str, str):
			d1 = self._parse_date(date)
			d = datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]))
			d += timedelta(days=duration)
			d2 = self._parse_date(
				d.year + d.month + d.day + date[8:20])
			return d1, d2




class QueryBuilder:

	SELECT 		= "SELECT {0} FROM {1}"
	USER_COND 	= " WHERE username LIKE '{0}'"
	INSERT 		= "INSERT INTO {0} VALUES ({1})"

	@staticmethod
	def find_user(username) -> str:
		return 	QueryBuilder.SELECT.format("username", "user") + QueryBuilder.USER_COND.format(username) + ";"

	@staticmethod
	def retrieve_hash(username) -> str:
		return 	QueryBuilder.SELECT.format("password", "user") + QueryBuilder.USER_COND.format(username) + ";"

	@staticmethod
	def add_user(username, password, first="", last="", email=""):
		fields = "'{u}', '{p}'"
		if first:
			fields += ", '{f}'"
		else:
			fields += "NULL"
		if last:
			fields += ", '{l}'"
		else:
			fields += "NULL"
		if email:
			fields += ", '{e}'"
		else:
			fields += "NULL"
		fields = fields.format(u=username, p=password, f=first, l=last, e=email)
		return QueryBuilder.INSERT.format(" user (username, password, firstname, lastname, email)", fields) + ";"

	@staticmethod
	def check_car_free(car_id):
		return "SELECT * FROM booking WHERE car_id LIKE '{0}';".format(car_id)

	@staticmethod
	def get_car(car_id):
		return "SELECT * FROM car WHERE id LIKE '{0}';".format(car_id)

	@staticmethod
	def update_lastlogin(username):
		return "UPDATE user SET lastlogin=CURRENT_TIMESTAMP() WHERE username LIKE '{0}';".format(username)

	@staticmethod
	def get_car_history(username):
		"""show a list of cars that current user has booked"""
		q = "SELECT m.model FROM model m, booking b, user u, car c WHERE u.username LIKE '{0}' "
		j = "AND c.id=b.car_id AND u.id=b.user_id AND c.model_id=m.id;"
		return q.format(username) + j

	@staticmethod
	def search_car(display_fields, **kwargs):
		"""search by any of the car’s properties and display fields"""
		fields = ["id", "registration", "make", "model", "colour", "seats", "location"]
		f = "*"
		for field in display_fields:
			if field not in fields:
				raise AttributeError("{0} not a valid field".format(field))
			if f=="*":
				f = field
			else:
				f += ", {0}".format(field)
		q = "SELECT {0} FROM car c, make ma, model mo, location l ".format(f)
		j = "WHERE c.make_id=ma.id AND c.model_id=mo.id AND c.location_id=l.id "
		s = ""
		for field in kwargs:
				if field not in fields:
					raise AttributeError("{0} not a valid search field".format(field))
				if field=="make":
					field = "ma.make"
				elif field=="model":
					field = "mo.model"
				elif field=="location":
					field = "l.location"
				s += "AND {0} LIKE {1} ".format(field, kwargs[field])
		return q + j + s + ";"

	@staticmethod
	def get_history(username):
		q1 = "SELECT u.username, mo.model, c.id, b.booked, l.location, b.duration, b.returned " 
		q2 = "FROM booking b, user u, car c, model mo, location l "
		j1 = "WHERE b.user_id=u.id AND b.car_id=c.id "
		j2 = "AND u.username LIKE '{0}'".format(username)
		return q1 + q2 + j1 + j2 + ";"

	@staticmethod
	def get_user_info(username):
		return "SELECT * FROM user WHERE username LIKE '{0}';".format(username)

	@staticmethod
	def load_commands(fp) -> list:
		"""Reads an sql file input and returns a list of commands to execute"""
		with open(fp, "r") as file:
			commands = []
			current = file.readline().strip()
			while current:
				while current[-1] != ";":
					_ = current
					current += file.readline().strip()
					if _==current:
						break
				commands.append(current)
				current = file.readline().strip()
			return commands

	@staticmethod
	def make_booking(self, **kwargs):
		k = {"event_id":0, "user_id":0, "car_id":0, "booked":"YYYYMMDD 00:00:00 AM", "duration":0}
		for key in k:
			if key not in kwargs:
				kwargs[key] = k[kwargs]
		q = "INSERT INTO booking(event_id, user_id, car_id, booked, duration) VALUES ({event_id}, {user_id}, {car_id}, {booked}, {duration});"
		return q.format(**kwargs)

	@staticmethod
	def finish_booking(event_id):
		return "UPDATE booking SET returned=CURRENT_TIMESTAMP();"
		

class ValueNotFound(Exception):
	pass


def main():
	pass


if __name__=="__main__":
	main()