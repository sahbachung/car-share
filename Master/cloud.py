import os
import pickle

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from google.auth.transport.requests import Request


class CloudCursor:

    SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
    creds = None
    service = None

    def __init__(self, **kwargs):
        self.service = self.get_service(**kwargs)

    def get_service(self, **kwargs):
        if os.path.exists(kwargs.get("token", "Master/cloud_token.pickle")):
            with open(kwargs.get("token", "Master/cloud_token.pickle"), "rb") as token:
                self.creds = pickle.load(token)
        if not self.creds:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                self.creds = ServiceAccountCredentials.from_json_keyfile_name(
                    filename=kwargs.get("credentials", "Master/credentials.json"),
                    scopes=self.SCOPES)
        return build("cloud_sql", "v3", credentials=self.creds)

    def execute(self, q):...

    def fetchall(self) -> list:...