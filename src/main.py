from pathlib import Path
#Cyclopts imports for easy CLI app
from cyclopts import App
#google imports to connect google api
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

DEBUG = False
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/tasks"]
BASE_DIR = Path(__file__).resolve().parent
TOKEN_PATH = BASE_DIR / "token.json"
CREDENTIALS_PATH = BASE_DIR / "credentials.json"


app = App()



def load_saved_credentials():
    """Load saved Google credentials from token.json, if available and readable."""
    if not TOKEN_PATH.exists():
        return None

    try:
        return Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    except ValueError:
        # token.json exists but is malformed or incompatible.
        TOKEN_PATH.unlink(missing_ok=True)
        return None


def run_authorization_flow():
    """Run the browser-based Google authorization flow and return new credentials."""
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(
            "credentials.json was not found next to main.py. "
            "Download it from Google Cloud Console and place it beside main.py."
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
    return flow.run_local_server(port=0)


def save_credentials(creds):
    """Persist credentials for future runs."""
    TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")


def get_service():
    """
    Build and return an authenticated Google Tasks API service.

    If the saved token is expired but refreshable, it is refreshed.
    If Google rejects the refresh because the token was expired or revoked,
    the bad token is deleted and the user is asked to authorize again.
    """
    creds = load_saved_credentials()

    if creds and creds.valid:
        return build("tasks", "v1", credentials=creds)

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except RefreshError:
            print(
                "Your saved Google authorization is no longer valid. "
                "Starting sign-in again..."
            )
            TOKEN_PATH.unlink(missing_ok=True)
            creds = run_authorization_flow()
    else:
        creds = run_authorization_flow()

    if not creds or not creds.valid:
        raise RuntimeError("Could not obtain valid Google credentials.")

    save_credentials(creds)
    return build("tasks", "v1", credentials=creds)


def get_tasklists(service):
  """Return all task lists."""
  results = service.tasklists().list(maxResults=100).execute()
  return results.get("items", [])

def get_tasklist_id_by_title(service, title: str):
  """Return a task list ID by title, or None if not found."""
  for tasklist in get_tasklists(service):
    if tasklist["title"] == title:
      return tasklist["id"]

  return None

def prompt_for_tasklist(service, prompt: str = "Please enter the title of the task list: "):
  """Show task lists, ask for a title, and return the title and ID."""
  print_tasklists(service)

  tasklist_name = input(prompt).strip()
  tasklist_id = get_tasklist_id_by_title(service, tasklist_name)

  if not tasklist_id:
    print(f"No task list found with the title '{tasklist_name}'.")
    return None, None

  return tasklist_name, tasklist_id

def resolve_tasklist(service, tasklist_name: str | None, prompt: str):
  """Resolve a task list name into a title and ID."""
  if not tasklist_name:
    return prompt_for_tasklist(service, prompt)

  tasklist_id = get_tasklist_id_by_title(service, tasklist_name)

  if not tasklist_id:
    print(f"No task list found with the title '{tasklist_name}'.")
    return None, None

  return tasklist_name, tasklist_id


def print_tasklists(service):
  """Print all task lists with their IDs and task counts."""
  tasklists = get_tasklists(service)

  if not tasklists:
    print("No task lists found.")
    return

  for tasklist in tasklists:
    results = service.tasks().list(tasklist=tasklist["id"]).execute()
    tasks = results.get("items", [])
    print(f"{tasklist['title']} (ID: {tasklist['id']}) tasks in list: {len(tasks)}")


def welcome_msg():
  service = get_service()

  print(
    "Hello, welcome to ClITasks. This application connects to your Google "
    "Tasks, allowing you to view, add, and remove tasks or task lists.\n"
  )
  print("Your current task lists are:\n")

  print_tasklists(service)

  print(
    "\nTo add a new task, run:"
    "\n  python main.py insert-task"
    "\n\nTo add a new task list, run:"
    "\n  python main.py insert-tasklist"
  )

@app.command
def get_tasks(tasklist_name: str | None = None):
    """Print tasks from a specific task list."""
    service = get_service()

    tasklist_name, tasklist_id = resolve_tasklist(
        service,
        tasklist_name,
        "Please enter the title of the task list: ",
    )

    if not tasklist_id:
        return

    results = service.tasks().list(tasklist=tasklist_id).execute()
    tasks = results.get("items", [])

    if not tasks:
        print("There are no tasks in this list.")
        return

    for task in tasks:
        print(task["title"])


@app.command
def insert_task(tasklist_name: str | None = None, task_title: str | None = None):
    """Insert a new task into a task list."""
    service = get_service()

    tasklist_name, tasklist_id = resolve_tasklist(
        service,
        tasklist_name,
        "Please enter the title of the task list: ",
    )

    if not tasklist_id:
        return

    if not task_title:
        task_title = input("What will the task be called? ").strip()

    if not task_title:
        print("Task title cannot be empty.")
        return

    task_details = {"title": task_title}
    new_task = service.tasks().insert(tasklist=tasklist_id, body=task_details).execute()

    print(f"'{new_task['title']}' has been added to '{tasklist_name}'.")


@app.command
def clear_task(tasklist_name: str | None = None):
    """Clear completed tasks from a task list."""
    service = get_service()

    tasklist_name, tasklist_id = resolve_tasklist(
        service,
        tasklist_name,
        "Please enter the title of the task list: ",
    )

    if not tasklist_id:
        return

    service.tasks().clear(tasklist=tasklist_id).execute()
    print(f"Completed tasks have been cleared from '{tasklist_name}'.")


@app.command
def get_tasklist():
    """Print all task lists."""
    service = get_service()
    print_tasklists(service)


@app.command
def insert_tasklist(list_title: str | None = None):
    """Create a new task list."""
    service = get_service()

    if not list_title:
        list_title = input("What is the task list name? ").strip()

    if not list_title:
        print("Task list title cannot be empty.")
        return

    list_details = {"title": list_title}
    new_tasklist = service.tasklists().insert(body=list_details).execute()

    print(f"You have added '{new_tasklist['title']}' as a new task list.")


@app.command
def delete_tasklist(tasklist_name: str | None = None):
    """Delete a task list after confirmation."""
    service = get_service()

    tasklist_name, tasklist_id = resolve_tasklist(
        service,
        tasklist_name,
        "Please enter the title of the task list you would like to delete: ",
    )

    if not tasklist_id:
        return

    results = service.tasks().list(tasklist=tasklist_id).execute()
    tasks = results.get("items", [])

    if not tasks:
        confirmation = input(
            "There are no tasks in this list. Delete it? This cannot be undone. [y/N] "
        ).strip().lower()

        if confirmation not in {"y", "yes"}:
            print("Delete cancelled.")
            return
    else:
        confirmation_name = input(
            f"Are you sure you would like to delete '{tasklist_name}'? "
            f"There are {len(tasks)} tasks in this list. "
            "Type the task list name to confirm: "
        ).strip()

        if confirmation_name != tasklist_name:
            print("Delete cancelled.")
            return

    service.tasklists().delete(tasklist=tasklist_id).execute()
    print(f"Deleted task list: '{tasklist_name}'.")


@app.default
def main():
    """Default CLI entry point."""
    try:
        welcome_msg()
    except HttpError as err:
        if DEBUG:
            print(err)
        else:
            print("Sorry, couldn't connect to Google Tasks.")


if __name__ == "__main__":
  app()