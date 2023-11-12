from gtasks.task_service import TaskService, TaskList, Task
from gspreadsheets.spreadsheet_service import SheetService, Sheet
from creds_provider import get_creds
import yaml
import pandas as pd

from planner import Planner
from meal_entry import MealEntry

import datetime

config = yaml.load(open("planner.yaml", "r"), Loader=yaml.FullLoader)

CREDS = get_creds()

task_service = TaskService(CREDS)
sheets_service = SheetService(CREDS)

def get_tasklist():
        
    task_list = task_service.get_tasklist_by_name("Meal Planner")
    if task_list is None:
        task_list = task_service.create_tasklist("Meal Planner")
    return task_list

def get_sheet():


    spreadsheet = sheets_service.get_spreadsheet_by_title("Meal Planner")
    if spreadsheet is None:
        spreadsheet = sheets_service.create_spreadsheet("Meal Planner")
    sheets = spreadsheet[2]

    for sheet in sheets:
        if sheet["sheet_title"] == "Meal Plan":
            return sheets_service.get_sheet(spreadsheet[0], sheet["sheet_title"])
            
    return sheets_service.add_sheet(spreadsheet[0], "Meal Plan")

task_list = get_tasklist()


planner = Planner('entries.jsonl', task_list)

def str_to_datetime(s):
    return datetime.datetime.strptime(s, "%d/%m/%Y")


def get_main_spreadsheet():
    sheet = get_sheet().get_csv()
    # convert to dataframe
    # fill in missing values
    values = sheet.get("values", [])
    for i, row in enumerate(values[1:]):
        if len(row) < len(values[0]):
            values[i+1].extend([""] * (len(values[0]) - len(row)))

    df = pd.DataFrame(values[1:], columns=values[0])
    return df

def get_local_spreadsheet(columns):

    # load local csv
    try:
        # read nan as ""
        local_df = pd.read_csv("meal_plan.csv", na_filter=False)
    except FileNotFoundError:
        local_df = pd.DataFrame(columns=columns)

        local_df.to_csv("meal_plan.csv", index=False)

    return local_df


def sync():

    df = get_main_spreadsheet()
    local_df = get_local_spreadsheet(df.columns)
    print(df)
    
    for i, row in df.iterrows():
        # if there are no values for that day in the local csv
        if len(local_df) <= i:
            # get each column value that is not empty
            for meal in df.columns[1:]:
                if row[meal] != "":
                    # create a new task
                    meal_entry = MealEntry(recipe_name=row[meal], date=str_to_datetime(row["Date"]), meal=meal)
                    planner.add_to_plan(meal_entry)
        # if values in a row don't match
        else:
            # check which values are different
            for meal in df.columns[1:]:
                
                if row[meal] != local_df.iloc[i][meal]:

                    # if the value is empty
                    if row[meal] == "":
                        # delete the task
                        print("Deleting from plan", str_to_datetime(row["Date"]), meal)
                        planner.delete_from_plan(str_to_datetime(row["Date"]), meal)
                    else:
                        # if meal didn't exist before
                        if local_df.iloc[i][meal] == "":
                            # create a new task
                            meal_entry = MealEntry(recipe_name=row[meal], date=str_to_datetime(row["Date"]), meal=meal)
                            print("Adding to plan", meal_entry)
                            planner.add_to_plan(meal_entry)
                        else:
                            # update the task
                            meal_entry = MealEntry(recipe_name=row[meal], date=str_to_datetime(row["Date"]), meal=meal)
                            print("Updating plan", meal_entry)
                            planner.edit_entry(meal_entry)
    
    local_df = df.copy()

    local_df.to_csv("meal_plan.csv", index=False)
    

sync()