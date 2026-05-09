# CLI Google Tasks

A Python command-line app for managing Google Tasks from the terminal.

This app lets you interact with your Google Tasks lists without opening a browser. You can view task lists, inspect 
tasks, and manage your Google Tasks workflow through simple CLI commands.

## Features

- View Google Task lists
- View tasks in a selected task list
- Add tasks
- Delete tasks
- Create task lists
- Delete task lists
- Authenticate with the Google Tasks API

## Project Structure

```text
cli_google_tasks/
├── src/
│   ├── main.py
│   ├── credentials.json
│   └── token.json
├── .gitignore
└── README.md
```

## Requirements

- Python 3.13+
- A Google account
- Google Tasks API enabled in Google Cloud

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd cli_google_tasks
```

### 2. Create and activate a virtual environment

On Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

If the project has a `requirements.txt` file:

```bash
pip install -r requirements.txt
```

If the project does not have one yet, install the needed packages and then generate it:

```bash
pip install <package-name>
pip freeze > requirements.txt
```

## Google API Setup

### 1. Create a Google Cloud project

Go to the Google Cloud Console:

```text
https://console.cloud.google.com/
```

Create a new project or select an existing one.

### 2. Enable the Google Tasks API

In your Google Cloud project:

1. Go to **APIs & Services**
2. Open **Library**
3. Search for **Google Tasks API**
4. Click **Enable**

### 3. Create OAuth credentials

1. Go to **APIs & Services**
2. Open **Credentials**
3. Click **Create Credentials**
4. Choose **OAuth client ID**
5. Select the appropriate application type
6. Download the credentials file

Rename the downloaded file to:

```text
credentials.json
```

Place it inside the `src/` directory:

```text
src/credentials.json
```

## Authentication

The first time you run the app, it may open a browser window asking you to sign in with your Google account and approve access to Google Tasks.

After authentication, a local token file will be created:

```text
src/token.json
```

This allows the app to reuse your login session without asking you to authenticate every time.

## Important Security Notes

Do not commit local credential or token files to version control.

These files should remain private:

```text
src/credentials.json
src/token.json
```

Your `.gitignore` should include entries like:

```gitignore
.venv/
__pycache__/
src/credentials.json
src/token.json
```

## Usage

Run the app from the project root:

```bash
python src/main.py --help
```

This displays the available commands.

General command format:

```bash
python src/main.py <command>
```

Example commands may look like:

```bash
python src/main.py get-tasklists
python src/main.py get-tasks
python src/main.py add-task
python src/main.py delete-task
```

Some commands may accept arguments:

```bash
python src/main.py get-tasks "<task-list-name>"
```

To see help for a specific command:

```bash
python src/main.py <command> --help
```

## Example Workflow

```bash
python src/main.py get-tasklists
python src/main.py get-tasks "Personal"
python src/main.py add-task "Personal" "Buy groceries"
python src/main.py get-tasks "Personal"
```

## Recommended Future Improvements

Possible improvements for the app:

- Mark tasks as completed
- Edit task titles
- Add due dates
- Show overdue tasks
- Search tasks
- Restore recently deleted tasks
- Add local trash or revision history
- Improve task formatting
- Add numbered task selection
- Add a configuration file for default settings

## Troubleshooting

### Authentication does not work

Try deleting the local token file and running the app again:

```text
src/token.json
```

The app should prompt you to authenticate again.

### Google Tasks API errors

Check that:

- The Google Tasks API is enabled
- Your OAuth credentials are valid
- `credentials.json` is located in the correct directory
- Your Google account has access to Google Tasks

### Command not found

Run:

```bash
python src/main.py --help
```

to see the available commands.

## Development Notes

This app is organized as a command-line interface around the Google Tasks API.

A good pattern for adding new functionality is:

1. Resolve the selected task list
2. Call the Google Tasks API
3. Handle empty or missing results
4. Print clear output for the user
5. Avoid exposing internal IDs unless needed

## License
MIT License
