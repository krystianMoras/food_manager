from meal_entry import MealEntry
from pathlib import Path
from datetime import datetime
import json
from gtasks.task_service import TaskList, Task



class Planner:

    def __init__(self, entries_path: str, task_list:TaskList) -> None:
        
        self.entries_path = Path(entries_path)
        self.task_list = task_list

    def add_to_plan(self, meal_entry: MealEntry) -> None:

        task = Task(title=meal_entry.recipe_name, notes=meal_entry.meal, due=meal_entry.date)
        task = self.task_list.add_task(task)

        if task is None:
            raise ValueError("Task creation failed")
        
        meal_entry.task_id = task
        
        with open(self.entries_path, 'a') as f:
            f.write(meal_entry.model_dump_json() + '\n')

    def delete_from_plan(self, date: datetime, meal: str) -> None:

        # parse entries for date and meal
        entries = self.get_plan()
        
        removed_entry_i = None
        for i, entry in enumerate(entries):
            if entry.date == date and entry.meal == meal:
                removed_entry_i = i
                break

        self.task_list.delete_task(entries[removed_entry_i].task_id)
        entries.pop(removed_entry_i)
        # write entries back to file
        with open(self.entries_path, 'w') as f:
            for entry in entries:
                f.write(entry.model_dump_json() + '\n')

    def edit_entry(self, new_meal_entry: MealEntry) -> None:

        # parse entries for date and meal
        entries = self.get_plan()
        edited_entry_i = None
        for i, entry in enumerate(entries):
            if entry.date == new_meal_entry.date and entry.meal == new_meal_entry.meal:
                edited_entry_i = i
                break

        task = Task(id=entries[edited_entry_i].task_id, title=new_meal_entry.recipe_name, notes=new_meal_entry.meal, due=new_meal_entry.date)
        task = self.task_list.edit_task(task)
        entries[edited_entry_i].recipe_name = new_meal_entry.recipe_name

        # write entries back to file
        with open(self.entries_path, 'w') as f:
            for entry in entries:
                f.write(entry.model_dump_json() + '\n')


    def get_plan(self) -> list[MealEntry]:
        
        with open(self.entries_path, 'r') as f:
            entries = f.readlines()

        entries = [MealEntry.model_validate(json.loads(entry)) for entry in entries]

        return entries
    