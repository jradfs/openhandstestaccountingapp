from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('accounting_tasks.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  category TEXT NOT NULL,
                  due_date DATE,
                  priority TEXT,
                  status TEXT DEFAULT 'pending',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('accounting_tasks.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tasks ORDER BY due_date ASC')
    tasks = c.fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form['title']
    category = request.form['category']
    due_date = request.form['due_date']
    priority = request.form['priority']
    
    conn = sqlite3.connect('accounting_tasks.db')
    c = conn.cursor()
    c.execute('INSERT INTO tasks (title, category, due_date, priority) VALUES (?, ?, ?, ?)',
              (title, category, due_date, priority))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/update/<int:id>', methods=['POST'])
def update_status(id):
    status = request.form['status']
    conn = sqlite3.connect('accounting_tasks.db')
    c = conn.cursor()
    c.execute('UPDATE tasks SET status = ? WHERE id = ?', (status, id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=3000)