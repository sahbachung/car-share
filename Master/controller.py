from mysql.connector import MySQLConnection
from mysql.connector.errors import ProgrammingError
import re
import argparse


class Controller(MySQLConnection):

	def __init__(self, host="localhost", username="root", password="", db="DEBUG"):
		super().__init__(host=host, user=username, password=password)
		self.autocommit = True
		self.cu = self.cursor()
		if db:
			self.use(db)

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


	def register_user(self, username, password, first="", last="", email="") -> bool:
		print("register " + username)
		if not first: first = "NULL"
		if not last: last = "NULL"
		if not email: email = "NULL"
		if self.query_username(username):
			return False
		self.cu.execute(QueryBuilder.add_user(username, password, first, last, email))
		return True


class QueryBuilder:

	SELECT 		= "SELECT {0} FROM {1}"
	USER_COND 	= " WHERE username LIKE '{0}'"
	INSERT 		= "INSERT INTO {0} VALUES ({1})"
	UPDATE_LAST = "UPDATE user SET lastlogin=CURRENT_TIMESTAMP() WHERE username LIKE '{0}"

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
		print(QueryBuilder.INSERT.format(" user (username, password, firstname, lastname, email)", fields))
		return QueryBuilder.INSERT.format(" user (username, password, firstname, lastname, email)", fields)

	@staticmethod
	def update_lastlogin(username):
		return QueryBuilder.UPDATE_LAST.format(username)

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


def main():
	if True: #For later
		c = Controller()
		cu = c.cu
		cu.execute("USE test;")
		c.init_database("Master/schema.sql")
		cu.execute("show tables;")
		print(cu.fetchall())


if __name__=="__main__":
	main()