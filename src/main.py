import os.path
#Cyclopts imports for easy CLI app
from cyclopts import App
#google imports for auth to connect google Tasks api
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

DEBUG = False
app = App()

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/tasks"]
def check_creds():
  """Shows basic usage of the Tasks API.
    Prints the title and ID of the first 10 task lists.
    """

  # The file token.json stores the user's access and refresh tokens and is
  # created automatically when the authorization flow completes for the first
  # time.
  creds = None
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())
  return build("tasks", "v1", credentials=creds)


def welcome_msg():
  print(f"Hello, Welcome to ClITasks. This application connects to your google tasks allowing you to view, add, and remove tasks or tasklists.\n"
        f"Your current task list are: \n"
          )
  get_tasklist()
  print("\n\nIf you would like to add a new task or tasklist run python3 main.py add task, or python3 main.py add tasklist")

def get_task_list_by_title(title: str):
  service = check_creds()

  results = service.tasklists().list().execute()
  for item in results.get("items", []):
    if item["title"] == title:
      return item["id"]

  return None

# get_tasks will return the tasks you have in a specific task list if you do not provide a task list title, then it will prompt you with a
# list and for a title to find the list of tasks
@app.command
def get_tasks(task_name: str = None):
  service = check_creds()

  if not task_name:
    get_tasklist()

    task_name = input("please enter the title of the Task list: ")
    tasklist_id = get_task_list_by_title(task_name)
  else:
    tasklist_id = get_task_list_by_title(task_name)

  results = service.tasks().list(tasklist=tasklist_id).execute()
  list_items = results.get("items",[])
  if not list_items:
    print("There are no tasks in list")
  for item in list_items:
    print(f"{item['title']}")

# get_tasks will return a printed list of the task list you have
@app.command
def get_tasklist():
  service = check_creds()

  # Call the Tasks API
  results = service.tasklists().list(maxResults=10).execute()
  items = results.get("items", [])

  if not items:
    print("No task lists found.")
    return

  for item in items:
    results = service.tasks().list(tasklist=item['id']).execute()
    tasks = results.get("items", [])
    print(f"{item['title']} ({item['id']}) tasks in list: {len(tasks)}")

@app.command
def delete_tasklist(tasklist_name: str =None):
  service = check_creds()

  if not tasklist_name:
    get_tasklist()

    tasklist_name = input("please enter the title of the Task list you would like to delete: ")
    tasklist_id = get_task_list_by_title(tasklist_name)
  else:
    tasklist_id = get_task_list_by_title(tasklist_name)

  results = service.tasks().list(tasklist=tasklist_id).execute()
  list_items = results.get("items", [])
  if not list_items:
    confirmation = input("There are no tasks in list... Y/N if you would like to delete list(This cannot be undone)")
    if confirmation == 'y' or 'Y' or 'yes' or 'Yes':
      print(f"Deleting Task list: {tasklist_name}")
      service.tasklists().delete(tasklist=tasklist_id).execute()
  else:
    confirmation_name = input(f"Are you sure you would like to delete {tasklist_name} there are: {len(list_items)} tasks in {tasklist_name}... Please type the name of the task list to delete. ")
    if confirmation_name == tasklist_name:
      service.tasklists().delete(tasklist=tasklist_id).execute()

@app.default
def main():
  #The main function is called from cli this is the default function if no commands are called after
  try:
    welcome_msg()




  except HttpError as err:
    if DEBUG:
      print(err)
    else:
      print("Sorry couldn't connect to Google.Tasks")


if __name__ == "__main__":
  app()