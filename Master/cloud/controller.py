from mysql.connector import MySQLConnection
import re

class Controller(MySQLConnection):

	def __init__(self, host, port, user, password):
		super().__init__(host=host, port=port, user=user, password=password)
		self.cursor = self.cursor()

	def init_database(self, schema_loc):
		with open("schema.sql", "r+") as file:
			# read file
			# remove whitespace
			# split into list by ';'
			# self.cursor.executemany(list)
			return


class QueryBuilder:

	SELECT = "SELECT %s FROM %s"
	INSERT = "INSERT INTO %s(%s) VALUES (%s)"

	@staticmethod
	def select(select, from_, where):...

	@staticmethod
	def insert(insert, into, values):...
