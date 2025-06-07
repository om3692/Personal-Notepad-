# app.py
import sqlite3
import datetime # Import the datetime module
from flask import Flask, render_template, request, redirect, url_for, g

# --- Application Setup ---
app = Flask(__name__) # Creates a Flask application instance
DATABASE = 'notepad_repository.db' # Name of our SQLite database file

# --- Database Helper Functions ---
def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()

def init_db(drop_existing=False):
    """Initializes the database schema (creates tables)."""
    db = get_db()
    if drop_existing:
        print("Dropping existing tables...")
        db.execute("DROP TABLE IF EXISTS items;")
        db.execute("DROP TABLE IF EXISTS subjects;")
        print("Tables dropped.") # Added confirmation

    print("Creating tables...")
    db.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    db.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL,
        item_type TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE
    );
    """)
    db.commit()
    # Removed "Database initialized successfully." print from here; CLI command will handle it.

@app.cli.command('init-db')
def init_db_command():
    """Clears existing data and creates new tables.""" # Improved docstring
    init_db(drop_existing=True)
    print('Database has been initialized.') # Consolidated success message for CLI

# --- Context Processor to make current_year available to all templates ---
@app.context_processor
def inject_current_year():
    """Makes the current year available in all templates."""
    return {'current_year': datetime.datetime.utcnow().year}

# --- Web Page Routes ---

@app.route('/')
def index():
    db = get_db()
    cursor = db.execute('SELECT id, name FROM subjects ORDER BY name ASC')
    subjects = cursor.fetchall()
    return render_template('index.html', subjects=subjects)

@app.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    if request.method == 'POST':
        # Correction: Use .get() for robustness and strip.
        name = request.form.get('name', '').strip()
        if name:
            db = get_db()
            try:
                db.execute('INSERT INTO subjects (name) VALUES (?)', (name,))
                db.commit()
                return redirect(url_for('index'))
            except sqlite3.IntegrityError:
                return render_template('add_subject.html', error="Subject name already exists.")
        else:
            return render_template('add_subject.html', error="Subject name cannot be empty.")
    return render_template('add_subject.html')

@app.route('/subject/<int:subject_id>')
def subject_detail(subject_id):
    db = get_db()
    subject_cursor = db.execute('SELECT id, name FROM subjects WHERE id = ?', (subject_id,))
    subject = subject_cursor.fetchone()
    if subject is None:
        return "Subject not found", 404
    items_cursor = db.execute(
        'SELECT id, item_type, title, content, created_at FROM items WHERE subject_id = ? ORDER BY created_at DESC',
        (subject_id,)
    )
    items = items_cursor.fetchall()
    return render_template('subject_detail.html', subject=subject, items=items)

@app.route('/subject/<int:subject_id>/add_item', methods=['GET', 'POST'])
def add_item(subject_id):
    db = get_db()
    subject_cursor = db.execute('SELECT id, name FROM subjects WHERE id = ?', (subject_id,))
    subject = subject_cursor.fetchone()
    if subject is None:
        return "Subject not found", 404

    if request.method == 'POST':
        # Correction: Use .get() for robustness and .strip() for all text fields.
        item_type = request.form.get('item_type', '').strip()
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()

        # Correction: More concise check for all fields being non-empty.
        if all((item_type, title, content)):
            db.execute(
                'INSERT INTO items (subject_id, item_type, title, content) VALUES (?, ?, ?, ?)',
                (subject_id, item_type, title, content)
            )
            db.commit()
            return redirect(url_for('subject_detail', subject_id=subject_id))
        else:
            return render_template('add_item.html', subject=subject, error="All fields are required.")
    return render_template('add_item.html', subject=subject)

@app.route('/item/<int:item_id>/delete', methods=['POST'])
def delete_item(item_id):
    db = get_db()
    item_cursor = db.execute('SELECT subject_id FROM items WHERE id = ?', (item_id,))
    item = item_cursor.fetchone()
    if item:
        subject_id = item['subject_id']
        db.execute('DELETE FROM items WHERE id = ?', (item_id,))
        db.commit()
        return redirect(url_for('subject_detail', subject_id=subject_id))
    return "Item not found or could not delete.", 404

@app.route('/subject/<int:subject_id>/delete', methods=['POST'])
def delete_subject(subject_id):
    db = get_db()
    # Correction: Check if subject exists before attempting to delete.
    subject_cursor = db.execute('SELECT id FROM subjects WHERE id = ?', (subject_id,))
    subject = subject_cursor.fetchone()
    if subject is None:
        return "Subject not found", 404

    db.execute('DELETE FROM subjects WHERE id = ?', (subject_id,))
    # Items associated with this subject will be deleted due to ON DELETE CASCADE
    db.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)