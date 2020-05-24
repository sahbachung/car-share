import os.path
import pickle
import re
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from mysql.connector import connect, ProgrammingError, InterfaceError

from base_type.controller import BaseController, LocalController
from base_type.query import BaseQuery


class Query(BaseQuery):
    SELECT = "SELECT {0} FROM {1}"
    USER_COND = " WHERE username LIKE '{0}'"
    INSERT = "INSERT INTO {0} VALUES ({1})"

    @staticmethod
    def find_user(username) -> str:
        return Query.SELECT.format("username", "user") + Query.USER_COND.format(username) + ";"

    @staticmethod
    def retrieve_hash(username) -> str:
        return Query.SELECT.format("password", "user") + Query.USER_COND.format(username) + ";"

    @staticmethod
    def add_user(username, password, first="", last="", email="") -> str:
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
        return Query.INSERT.format(" user (username, password, firstname, lastname, email)", fields) + ";"

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
            if f == "*":
                f = field
            else:
                f += ", {0}".format(field)
        q = "SELECT {0} FROM car c, make ma, model mo, location l ".format(f)
        j = "WHERE c.make_id=ma.id AND c.model_id=mo.id AND c.location_id=l.id "
        s = ""
        for field in kwargs:
            if field not in fields:
                raise AttributeError("{0} not a valid search field".format(field))
            if field == "make":
                field = "ma.make"
            elif field == "model":
                field = "mo.model"
            elif field == "location":
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
                    if _ == current:
                        break
                commands.append(current)
                current = file.readline().strip()
            return commands

    @staticmethod
    def make_booking(**kwargs):
        k = {"event_id": 0, "user_id": 0, "car_id": 0, "booked": "YYYYMMDD 00:00:00 AM", "duration": 0}
        for key in k:
            if key not in kwargs:
                kwargs[key] = k[key]
        q = "INSERT INTO booking(event_id, user_id, car_id, booked, duration)"
        v = " VALUES ('{event_id}', '{user_id}', '{car_id}', '{booked}', '{duration}');"
        return q + v.format(**kwargs)

    @staticmethod
    def get_bookings(username=None):
        q = "SELECT "

    @staticmethod
    def finish_booking(event_id):
        return "UPDATE booking SET returned=CURRENT_TIMESTAMP();"


class Controller(LocalController):
    CURRENT_DATABASE = None

    def __init__(self, **kwargs):
        super().__init__()
        self.config = kwargs
        print(self.config)
        if kwargs["database"]:
            self.use(kwargs["database"])
        self.credfile = kwargs.get("credentials", "Master/credentials.json")

    def __enter__(self):
        self._conn.autocommit = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cu.execute("COMMIT;")
        self._conn.autocommit = True
        pass

    def use(self, db):
        try:
            self.cu.execute(f"USE {db}")
        except ProgrammingError as ex:
            if "Y" == str.upper(input(f"ERROR: {ex}\nINITIALISE {db}? (Y/N): ")):
                self.init_database(self.config["schema"], db=db)
            else:
                exit(-1)

    def init_database(self, schema_loc, db="DEBUG", qb=Query):
        super().init_database(schema_loc, db=db, qb=qb)

    def query(self, q, n=1) -> tuple:
        self.cu.execute(q)
        result_set = self.cu.fetchall()
        if not result_set:
            return None,
        if n < 1:
            return tuple(result_set)
        elif n == 1:
            return result_set[0]
        elif n > 1:
            return tuple(result_set[:n])

    # DATABASE INTERFACE

    def query_username(self, username) -> bool:
        return bool(self.query(Query.find_user(username))[0])

    def verify_hash(self, username, key_hash) -> bool:
        q = self.query(Query.retrieve_hash(username))
        return bool(q) and q[0] == key_hash

    def login(self, username, password) -> bool:
        if not self.query_username(username) or not self.verify_hash(username, password):
            return False
        else:
            self.cu.execute(Query.update_lastlogin(username))
            return True

    def register_user(self, username, password, first="", last="", email="") -> bool:
        if not first:
            first = "NULL"
        if not last:
            last = "NULL"
        if not email:
            email = "NULL"
        if self.query_username(username):
            return False
        self.cu.execute(Query.add_user(username, password, first, last, email))
        return True

    def book_car(self, event_id, username, car_id, date, duration):
        # YYYYMMDD HH:MM:SS [AP]M
        Controller.parse_date(date)
        assert self.car_is_free(car_id)
        assert duration > 0
        q = Query.make_booking(
            event_id=event_id,
            user_id=self.get_user_details(username)[0],
            car_id=car_id, booked=date)

    @staticmethod
    def parse_date(d) -> (int, int, int, int, int, int):
        assert re.search("[0-9]{8} [0-9]{2}:[0-9]{2}:[0-9]{2} [AP]M", d)
        year = int(d[0:4])
        month = int(d[4:6])
        day = int(d[6:8])
        hour = int(d[9:11])
        minute = int(d[12:14])
        second = int(d[15:17])
        if d[-2] == "P":
            hour = (hour + 12) % 24
        return year, month, day, hour, minute, second

    def get_all_cars(self) -> tuple:
        self.cu.execute(Query.search_car([]))
        return self.cu.fetchall()

    def search_cars(self, display_fields=None, **kwargs):
        return self.query(Query.search_car(display_fields, **kwargs), n=-1)

    def get_history(self, username) -> tuple:
        return self.query(Query.get_history(username))

    def get_user_details(self, username) -> tuple:
        return self.query(Query.get_user_info(username))

    def get_next_event_id(self) -> int:
        eid = self.query("SELECT MAX(event_id) FROM booking;")
        if not eid:
            return 0
        else:
            return int(eid[0]) + 1

    def get_email(self, user) -> str:

        r = self.query("SELECT email FROM user WHERE username LIKE '{0}'".format(user))
        if not r:
            raise ValueNotFound
        else:
            return r[0]

    def get_car(self, car_id) -> bool:
        return bool(self.query(Query.get_car(car_id)))

    def car_is_free(self, car_id) -> bool:
        if not self.get_car(car_id):
            return False
        return not bool(self.query(Query.check_car_free(car_id)))

    def get_user_bookings(self, user=None):
        pass


class Calendar:
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = None
    pkl = "car-share/Master/token.pickle"
    credentials = "car-share/Master/credentials.json"

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
        email = self.controller.get_email(user)
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
        self.controller.book_car(event_id, user, car_id, date, duration)
        return True

    def _parse_dates(self, date, duration) -> (str, str):
        d1 = self.controller.parse_date(date)
        d = datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]))
        d += timedelta(days=duration)
        d2 = self.controller.parse_date(
            d.year + d.month + d.day + date[8:20])
        return d1, d2


class ValueNotFound(Exception):
    pass


def main():
    pass


if __name__ == "__main__":
    main()
