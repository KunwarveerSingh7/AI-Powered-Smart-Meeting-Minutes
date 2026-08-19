# AI-Powered-Smart-Meeting-Minutes
AI-Powered Smart Meeting Minutes and Task Tracker developed using Python, FastAPI, SQLite and Ollama.

# Team Members
Kunwarveer Singh Cheema
Mohammad Rayyan
Emmanuel Obi
Manuel Garcia


# Technologies used
Python
Fast API
SQLite
HTML
CSS
JavaScript
Bootstrap
Ollama
Llama 3
Github

# Features
Role Based Login system

## Manager
- create employee accounts
- upload meeting minutes in pdf/docx/or txt format
- uploded document processed by AI analysis
- review and edit generated summary, decisions, and tasks
- assign tasks to the employees
- publish the meeting
- monitor task and employee analytics

## Employee
- view personal analytics
- view assigned tasks
- update the task status
- view published meeting (information includes meeting summary, decisions, and extracted notes)
- review completed tasks in task history


# Instructions
1. before running the application ensure that following are installed:
- Python 3 - https://www.python.org/downloads/
- Ollama - https://ollama.com/download/windows
- Git - https://git-scm.com/install/windows

2. Clone the repsitory from github or download it as a zip file. Open the project folder on Visual Studio Code.

3. Install all of the python dependencies
- open a terminal in the project directory
pip install -r requirements.txt

4. The project uses llama 3 model for local ai processing. which is why it needs to be installed
- first install it on your computer as per the first instruction
- then run this command on the terminal
- "ollama pull llama3"

- once ollama is installed make sure it is running as it is vital for this application
- run this command on terminal
- ollama list

- if it returns something similar to this it means it is running
- NAME             ID              SIZE      MODIFIED      
- llama3:latest    365c0bd3c000    4.7 GB    3 minutes ago 

- if it doesnt return anything start it with this command and check using last command again
- ollama serve

5. before using the application, the initial manager account needs to be created
- open the backend directory on the terminal with this command
- cd backend
- then run the manager setup file on the same terminal
- python manager_handle.py
- manager credentials generated are shown on the terminal itself

6. now everything required to run this application has been setup and installed
- run this command inside the backend directory
- python -m uvicorn main:app --reload

7. once the terminal shows that the application is running
- open the login page on the web browser using this link
- http://127.0.0.1:8000/login-page
- the manager can log in using the credentials generated earlier which are also printed on to the terminal

8. to check if the backend is running go to this link
- http://127.0.0.1:8000

9. the FastAPI Swagger documentation can be accessed at
- http://127.0.0.1:8000/docs

10. Suggestion: sample meeting data that can be used for testing the application is in the folder tests/test_material. also read the file TESTING.md





