from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

import yaml
from pathlib import Path


def get_creds():
    config = yaml.load(open("planner.yaml", "r"), Loader=yaml.FullLoader)

    SCOPES = [
        "https://www.googleapis.com/auth/tasks",
        "https://www.googleapis.com/auth/drive.file",
    ]

    token_path = config["token"]
    credentials_path = config["credentials"]

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if Path(token_path).exists():
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES
            )
            creds = flow.run_local_server(port=0)

    with open(token_path, "w") as token:
        token.write(creds.to_json())

    return creds
