StudyHub - A Flask Notepad Application
StudyHub is a simple, clean, and modern web application built with Flask and styled with Tailwind CSS. It's designed to be a personal repository for organizing study materials, notes, and resources by subject.

Features
Subject Management: Create, view, and delete subjects to categorize your notes.
Item Management: Add various types of items to each subject, including plain notes, web links, and video references.
Data Persistence: All your data is stored locally in a SQLite database (notepad_repository.db).
Cascade Deletion: Deleting a subject automatically deletes all of its associated items, keeping your database clean.
Modern UI: A responsive and visually appealing interface built with Tailwind CSS.
CLI for Setup: Includes a simple command-line interface command (flask init-db) to set up the database schema.
Screenshots
(Here you could include screenshots of the application, such as the home page, a subject detail page, and the "add item" form.)

Home Page:

Subject Detail Page:

Technology Stack
Backend: Python, Flask
Database: SQLite
Frontend: HTML, Tailwind CSS (via CDN)
Getting Started
Follow these instructions to set up and run the project on your local machine.

Prerequisites
Python 3.x
pip (Python package installer)
Installation
Clone the repository:

Bash

git clone <your-repository-url>
cd MyNotepadApp
Create and activate a virtual environment (recommended):

Bash

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
py -m venv venv
.\venv\Scripts\activate
Install the required dependencies:
The only external dependency is Flask.

Bash

pip install Flask
Running the Application
Initialize the Database:
Before running the app for the first time, you must create the database and its tables. From the root MyNotepadApp directory, run the following command in your terminal:

Bash

flask init-db
This command will create the notepad_repository.db file and set up the subjects and items tables.

Run the Flask Application:
Start the development server with:

Bash

python app.py
Access the Application:
Open your web browser and navigate to:

http://127.0.0.1:5000

