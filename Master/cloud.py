import json
import os
import pickle

from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


def build_credentials(path) -> dict:
    with open(path, "rb") as creds:
        return json.load(creds)


class CloudCursor:
    SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
    creds = None
    credentials = {}
    service = None

    def __init__(self, **kwargs):
        self.service = self.get_service(**kwargs)
        self.credentials = build_credentials(kwargs.get("credentials", "car-share/Master/credentials.json"))

    def get_service(self, **kwargs):
        if os.path.exists(kwargs.get("token", "car-share/Master/cloud_token.pickle")):
            with open(kwargs.get("token", "car-share/Master/cloud_token.pickle"), "rb") as token:
                self.creds = pickle.load(token)
        if not self.creds:
            if self.creds and self.creds.refresh_token:
                self.creds.refresh(Request())
            elif self.credentials:
                self.creds = ServiceAccountCredentials.from_json_keyfile_dict(
                    self.credentials, scopes=self.SCOPES
                )
        return build("cloud_sql", "v3", credentials=self.creds)

    def execute(self, q):
        ...

    def fetchall(self) -> list:
        ...
