from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pathlib import Path
import json

class SheetService:

    def __init__(self, creds) -> None:
        # create service
        self.service = build("sheets", "v4", credentials=creds)

        self.spreadsheets_json = Path(__file__).parent / "spreadsheets.json"
        if not self.spreadsheets_json.exists():
            with open(self.spreadsheets_json, "w") as f:
                json.dump([], f)
        with open(self.spreadsheets_json, "r") as f:
            self.spreadsheets = json.load(f)

    def create_spreadsheet(self, title):
        # pylint: disable=maybe-no-member
        try:
            spreadsheet = {"properties": {"title": title}}
            spreadsheet = (
                self.service.spreadsheets()
                .create(body=spreadsheet, fields="spreadsheetId")
                .execute()
            )
            print(f"Spreadsheet ID: {(spreadsheet.get('spreadsheetId'))}")

            self.spreadsheets.append({
                "spreadsheet_id": spreadsheet["spreadsheetId"],
                "title": title,
                "sheets": []
            })

            with open(self.spreadsheets_json, "w") as f:
                json.dump(self.spreadsheets, f)

            return spreadsheet["spreadsheetId"], title, []
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error

    def _parse_spreadsheet_properties(self, spreadsheet_id):
            
        try:
            result = (
                self.service.spreadsheets()
                .get(spreadsheetId=spreadsheet_id)
                .execute()
            )
            title = result["properties"]["title"]
            sheets = []
            if "sheets" in result:
                for sheet in result["sheets"]:
                    sheet_id = sheet["properties"]["sheetId"]
                    sheet_title = sheet["properties"]["title"]
                    sheets.append({
                        "sheet_id": sheet_id,
                        "sheet_title": sheet_title
                    })

            return {
                "spreadsheet_id": spreadsheet_id,
                "title": title,
                "sheets": sheets
            }

        except HttpError as error:
            print(f"An error occurred: {error}")
            return error

    def get_spreadsheet(self, spreadsheet_id):
        # pylint: disable=maybe-no-member
        # go through spreadsheets and check if id is present
        spreadsheet = None
        for i, spreadsheet in enumerate(self.spreadsheets):

            if spreadsheet["spreadsheet_id"] == spreadsheet_id:
                spreadsheet = self.spreadsheets[i]
                if "title" or "sheets" not in spreadsheet:
                    self.spreadsheets[i] = self._parse_spreadsheet_properties(spreadsheet_id)
                    with open(self.spreadsheets_json, "w") as f:
                        json.dump(self.spreadsheets, f)
                break

            else:
                self.spreadsheets[i] = self._parse_spreadsheet_properties(spreadsheet_id)
                spreadsheet = self.spreadsheets[i]

                with open(self.spreadsheets_json, "w") as f:
                    json.dump(self.spreadsheets, f)

                break

        return spreadsheet_id, spreadsheet["title"], spreadsheet["sheets"]
    

    def get_spreadsheet_by_title(self, spreadsheet_title):
        for spreadsheet in self.spreadsheets:
            if spreadsheet["title"] == spreadsheet_title:
                return spreadsheet["spreadsheet_id"], spreadsheet_title, spreadsheet["sheets"]
            
        return None

    def add_sheet(self, spreadsheet_id, sheet_name):
        # pylint: disable=maybe-no-member
        try:
            body = {"requests": [{"addSheet": {"properties": {"title": sheet_name}}}]}

            result = (
                self.service.spreadsheets()
                .batchUpdate(spreadsheetId=spreadsheet_id, body=body)
                .execute()
            )
            sheet_id = result["replies"][0]["addSheet"]["properties"]["sheetId"]
            
            for i, spreadsheet in enumerate(self.spreadsheets):

                if spreadsheet["spreadsheet_id"] == spreadsheet_id:
                    self.spreadsheets[i]["sheets"].append({
                        "sheet_id": sheet_id,
                        "sheet_title": sheet_name
                    })

                    with open(self.spreadsheets_json, "w") as f:
                        json.dump(self.spreadsheets, f)

                    break

    
            return Sheet(self.service, spreadsheet_id, sheet_id, sheet_name)
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error

    def get_sheet(self, spreadsheet_id, sheet_name):
        print(spreadsheet_id, sheet_name)
        for spreadsheet in self.spreadsheets:
            if spreadsheet["spreadsheet_id"] == spreadsheet_id:
                for sheet in spreadsheet["sheets"]:
                    if sheet["sheet_title"] == sheet_name:
                        return Sheet(self.service, spreadsheet_id, sheet["sheet_id"], sheet_name)
        return None


class Sheet:

    def __init__(self, sheet_service, spreadsheet_id, sheet_id, sheet_name) -> None:
        self.spreadsheet_id = spreadsheet_id
        self.sheet_id = sheet_id
        self.sheet_service = sheet_service

        self.sheet_name = sheet_name

    def import_csv(self, csv_data):

        try:
            body = {
                "requests": [
                    {
                        "pasteData": {
                            "coordinate": {
                                "sheetId": self.sheet_id,
                                "rowIndex": 0,
                                "columnIndex": 0,
                            },
                            "data": csv_data,
                            "type": "PASTE_NORMAL",
                            "delimiter": ",",
                        }
                    }
                ]
            }

            result = (
                self.sheet_service.spreadsheets()
                .batchUpdate(spreadsheetId=self.spreadsheet_id, body=body)
                .execute()
            )
            return result
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error
        

    def get_csv(self):
        # pylint: disable=maybe-no-member
        try:
            result = (
                self.sheet_service.spreadsheets()
                .values()
                .get(spreadsheetId=self.spreadsheet_id, range=self.sheet_name)
                .execute()
            )
            return result
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error


if __name__ == "__main__":
    from creds_provider import get_creds
    from pathlib import Path
    import json

    # open spreadsheets.json which is on the same level as this file


    # get the spreadsheet id from the json


    creds = get_creds()
    service = SheetService(creds)

    spreadsheet_id, spreadsheet_title, sheets = service.create_spreadsheet("Meal Planner")

    sheet = service.add_sheet(spreadsheet_id, "Meal Plan")

    print(spreadsheet_id, spreadsheet_title, sheets)

    