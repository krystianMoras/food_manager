
from googleapiclient.discovery import build

from googleapiclient.errors import HttpError
from typing_extensions import Annotated
from pydantic import BaseModel, field_serializer, BeforeValidator
from datetime import datetime


class Task(BaseModel):
    id: str = None
    title: str
    due: Annotated[datetime, BeforeValidator(lambda string: datetime.fromisoformat(string) if type(string) == str else string)]
    status: str = None
    notes: str
    completed: Annotated[datetime, BeforeValidator(lambda string: datetime.fromisoformat(string) if type(string) == str else string)] = None

    @field_serializer('due')
    def serialize_due(self, value):
        return value.isoformat() + 'Z'  
    
    @field_serializer('completed')
    def serialize_completed(self, value):
        return value.isoformat() + 'Z'


class TaskList:

    def __init__(self, service, task_list_id, task_list_name) -> None:
        self.task_list_id = task_list_id
        self.task_list_name = task_list_name
        self.service = service

    def add_task(self, task: Task):
        response = self.service.tasks().insert(tasklist=self.task_list_id, body=task.model_dump(exclude_none=True)).execute()
        
        return Task(**response)

    def get_task(self, task_id: str):
        response = self.service.tasks().get(tasklist=self.task_list_id, task=task_id).execute()
        return Task(**response)

    def edit_task(self, task: Task):
        response = self.service.tasks().update(tasklist=self.task_list_id, task=task.id, body=task.model_dump(exclude_none=True)).execute()
        return Task(**response)

    def delete_task(self, task_id: str):
        response = self.service.tasks().delete(tasklist=self.task_list_id, task=task_id).execute()
        return response

    def get_tasks(self):
        response = self.service.tasks().list(tasklist=self.task_list_id).execute()

        tasks = []

        for task in response.get("items", []):
            tasks.append(Task(**task))

        return tasks

class TaskService:

    def __init__(self, creds) -> None:

        self.service = build('tasks', 'v1', credentials=creds)
        self.task_lists = []
        self._get_tasklists()

    def _get_tasklists(self):
        try:
            # Call the Tasks API
            results = self.service.tasklists().list().execute()
            items = results.get("items", [])

            if not items:
                self.task_lists = []
            else:
                self.task_lists = items

        except HttpError as err:
            print(err)

        finally:
            return self.task_lists
        
        
    def get_tasklist_by_name(self, task_list_name:str):
        for task_list in self.task_lists:
            if task_list['title'] == task_list_name:
                return TaskList(self.service, task_list['id'], task_list['title'])
        return None
    
    def get_tasklist_by_id(self, task_list_id:str):
        for task_list in self.task_lists:
            if task_list['id'] == task_list_id:
                return TaskList(self.service, task_list['id'], task_list['title'])
        return None
    
