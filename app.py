from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Initialize the database
def init_db():
    conn = sqlite3.connect('schedule.db')
    c = conn.cursor()
    # Create Employees table
    c.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    # Create Shifts table
    c.execute('''
        CREATE TABLE IF NOT EXISTS shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            day_of_week TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route("/")
def index():
    # Manager dashboard: View all employees
    conn = sqlite3.connect('schedule.db')
    c = conn.cursor()
    c.execute("SELECT * FROM employees")
    employees = c.fetchall()
    conn.close()
    return render_template("index.html", employees=employees)

@app.route("/employee/<int:employee_id>")
def view_employee_schedule(employee_id):
    # View an individual employee's weekly schedule
    conn = sqlite3.connect('schedule.db')
    c = conn.cursor()
    c.execute("SELECT name FROM employees WHERE id = ?", (employee_id,))
    employee_name = c.fetchone()[0]
    c.execute("SELECT day_of_week, start_time, end_time FROM shifts WHERE employee_id = ? ORDER BY day_of_week", (employee_id,))
    shifts = c.fetchall()
    conn.close()
    return render_template("employee.html", employee_name=employee_name, shifts=shifts)

@app.route("/add_employee", methods=["POST"])
def add_employee():
    # Add a new employee
    name = request.form.get("name")
    conn = sqlite3.connect('schedule.db')
    c = conn.cursor()
    c.execute("INSERT INTO employees (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/add_shift/<int:employee_id>", methods=["GET", "POST"])
def add_shift(employee_id):
    # Add a weekly shift for an employee
    if request.method == "POST":
        day_of_week = request.form.get("day_of_week")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        conn = sqlite3.connect('schedule.db')
        c = conn.cursor()
        c.execute("INSERT INTO shifts (employee_id, day_of_week, start_time, end_time) VALUES (?, ?, ?, ?)",
                  (employee_id, day_of_week, start_time, end_time))
        conn.commit()
        conn.close()
        return redirect(url_for("view_employee_schedule", employee_id=employee_id))
    else:
        return render_template("add_shift.html", employee_id=employee_id)

@app.route("/weekly_schedule")
def weekly_schedule():
    # View all employees' weekly schedules
    conn = sqlite3.connect('schedule.db')
    c = conn.cursor()
    c.execute("""
        SELECT employees.name, shifts.day_of_week, shifts.start_time, shifts.end_time 
        FROM shifts 
        JOIN employees ON shifts.employee_id = employees.id
        ORDER BY shifts.day_of_week, shifts.start_time
    """)
    weekly_shifts = c.fetchall()
    conn.close()
    return render_template("weekly_schedule.html", weekly_shifts=weekly_shifts)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)