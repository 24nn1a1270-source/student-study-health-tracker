from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            roll_number TEXT,
            course TEXT,
            year TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS study (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            hours REAL,
            date TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS todo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            done INTEGER DEFAULT 0
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS water (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            glasses INTEGER,
            date TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_name TEXT,
            done INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    conn = get_db_connection()

    if request.method == 'POST':
        name = request.form['name']
        roll_number = request.form['roll_number']
        course = request.form['course']
        year = request.form['year']

        conn.execute('DELETE FROM profile')
        conn.execute('INSERT INTO profile (name, roll_number, course, year) VALUES (?, ?, ?, ?)',
                     (name, roll_number, course, year))
        conn.commit()

    profile_data = conn.execute('SELECT * FROM profile').fetchone()
    conn.close()

    return render_template('profile.html', profile=profile_data)

@app.route('/study', methods=['GET', 'POST'])
def study():
    conn = get_db_connection()

    if request.method == 'POST':
        subject = request.form['subject']
        hours = request.form['hours']
        date = request.form['date']

        conn.execute('INSERT INTO study (subject, hours, date) VALUES (?, ?, ?)',
                     (subject, hours, date))
        conn.commit()

    all_sessions = conn.execute('SELECT * FROM study ORDER BY date DESC').fetchall()
    conn.close()

    return render_template('study.html', sessions=all_sessions)

@app.route('/todo', methods=['GET', 'POST'])
def todo():
    conn = get_db_connection()

    if request.method == 'POST':
        task = request.form['task']
        conn.execute('INSERT INTO todo (task, done) VALUES (?, 0)', (task,))
        conn.commit()

    all_tasks = conn.execute('SELECT * FROM todo ORDER BY id DESC').fetchall()
    conn.close()

    return render_template('todo.html', tasks=all_tasks)

@app.route('/todo/complete/<int:task_id>')
def complete_task(task_id):
    conn = get_db_connection()
    conn.execute('UPDATE todo SET done = 1 WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return redirect('/todo')

@app.route('/todo/delete/<int:task_id>')
def delete_task(task_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM todo WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return redirect('/todo')

@app.route('/water', methods=['GET', 'POST'])
def water():
    conn = get_db_connection()

    if request.method == 'POST':
        glasses = request.form['glasses']
        date = request.form['date']

        conn.execute('INSERT INTO water (glasses, date) VALUES (?, ?)', (glasses, date))
        conn.commit()

    all_logs = conn.execute('SELECT * FROM water ORDER BY date DESC').fetchall()
    conn.close()

    return render_template('water.html', logs=all_logs)

@app.route('/habits', methods=['GET', 'POST'])
def habits():
    conn = get_db_connection()

    if request.method == 'POST':
        habit_name = request.form['habit_name']
        conn.execute('INSERT INTO habits (habit_name, done) VALUES (?, 0)', (habit_name,))
        conn.commit()

    all_habits = conn.execute('SELECT * FROM habits ORDER BY id DESC').fetchall()
    conn.close()

    return render_template('habits.html', habits=all_habits)

@app.route('/habits/complete/<int:habit_id>')
def complete_habit(habit_id):
    conn = get_db_connection()
    conn.execute('UPDATE habits SET done = 1 WHERE id = ?', (habit_id,))
    conn.commit()
    conn.close()
    return redirect('/habits')

@app.route('/habits/reset/<int:habit_id>')
def reset_habit(habit_id):
    conn = get_db_connection()
    conn.execute('UPDATE habits SET done = 0 WHERE id = ?', (habit_id,))
    conn.commit()
    conn.close()
    return redirect('/habits')

@app.route('/habits/delete/<int:habit_id>')
def delete_habit(habit_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM habits WHERE id = ?', (habit_id,))
    conn.commit()
    conn.close()
    return redirect('/habits')

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()

    profile_data = conn.execute('SELECT * FROM profile').fetchone()

    total_study_hours = conn.execute('SELECT SUM(hours) FROM study').fetchone()[0] or 0

    total_tasks = conn.execute('SELECT COUNT(*) FROM todo').fetchone()[0]
    completed_tasks = conn.execute('SELECT COUNT(*) FROM todo WHERE done = 1').fetchone()[0]

    total_water_logs = conn.execute('SELECT COUNT(*) FROM water').fetchone()[0]
    avg_water = conn.execute('SELECT AVG(glasses) FROM water').fetchone()[0] or 0

    total_habits = conn.execute('SELECT COUNT(*) FROM habits').fetchone()[0]
    completed_habits = conn.execute('SELECT COUNT(*) FROM habits WHERE done = 1').fetchone()[0]

    conn.close()

    return render_template('dashboard.html',
                           profile=profile_data,
                           total_study_hours=total_study_hours,
                           total_tasks=total_tasks,
                           completed_tasks=completed_tasks,
                           total_water_logs=total_water_logs,
                           avg_water=round(avg_water, 1),
                           total_habits=total_habits,
                           completed_habits=completed_habits)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)