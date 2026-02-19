from flask import Flask, render_template, request, redirect, session,url_for
from flask_sqlalchemy import SQLAlchemy
from jobs_scraper import get_all_jobs
from vtu_scraper import fetch_vtu_updates
print("VTU test:",fetch_vtu_updates())


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'college_secret'
db = SQLAlchemy(app)

# --- Database Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(10))  # "teacher" or "student"

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    date = db.Column(db.String(50))
    description = db.Column(db.String(300))
    added_by = db.Column(db.String(100))

# --- Routes ---
@app.route('/')
def home():
    vtu_updates = fetch_vtu_updates()
    return render_template('login.html', vtu_updates=vtu_updates)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, password=password).first()

        if user:
            if user.role == 'teacher':
                session['user'] = email
                return redirect(url_for('teacher_dashboard'))
            else:
                session['user'] = email
                return redirect(url_for('student_dashboard'))
        return "Invalid login credentials!"

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']  # teacher or student

        # check if user already exists
        if User.query.filter_by(email=email).first():
            return "Account already exists — Please login"

        new_user = User(email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home'))  # or redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()       # remove session of teacher/student
    return redirect('/login')

@app.route('/teacher')
def teacher_dashboard():
    events = Event.query.all()
    return render_template("teacher_dashboard.html", events=events)

@app.route('/add_event', methods=['POST'])
def add_event():
    title = request.form['title']
    date = request.form['date']
    description = request.form['description']

    new_event = Event(title=title, date=date, description=description)
    db.session.add(new_event)
    db.session.commit()

    return redirect(url_for('teacher_dashboard'))

# ... (all your imports and models at the top) ...

# 🗑 DELETE EVENT ROUTE
@app.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    # ... (this was fine) ...
    event = Event.query.get(event_id)
    if event:
        db.session.delete(event)
        db.session.commit()
    return redirect(url_for('teacher_dashboard'))

# --- NOTIFICATION LOGIC ---
# REMOVED the duplicate 'generate_ai_notifications' function.
# We will modify 'generate_notifications' to be the only one you need.

from datetime import datetime, timedelta

def generate_notifications(events, vtu_updates, jobs):
    notifications = []
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    next3 = today + timedelta(days=3)

    # College event reminders
    for event in events:
        try:
            event_date = datetime.strptime(event.date, "%Y-%m-%d").date()
            days_left = (event_date - today).days

            if event_date == today:
                notifications.append(f"⚠ TODAY: '{event.title}' is happening now!")
            elif event_date == tomorrow:
                notifications.append(f"🔔 TOMORROW: '{event.title}' is tomorrow.")
            elif today < event_date <= next3:
                notifications.append(f"📌 AI Note: '{event.title}' is in {days_left} days — prepare!")
        except:
            continue

    # VTU notification — only once
    for update in vtu_updates:
        title = update["title"].lower()
        if "circular" in title:
            if "📄 New VTU circular published." not in notifications:
                notifications.append("📄 New VTU circular published.")

    # Job notification — only once
    if jobs and len(jobs) > 0:
        if "💼 New Job notification available." not in notifications:
            notifications.append("💼 New Job notification available.")

    return notifications

@app.route('/student')
def student_dashboard():
    events = Event.query.all()
    vtu_updates = fetch_vtu_updates()
    jobs= get_all_jobs()

    

    # --- THIS IS THE FIX ---
    # Call the correct, combined notification function
    notifications = generate_notifications(events, vtu_updates,jobs)

    print("VTU test:", vtu_updates)
    print("Job test:", jobs)

    return render_template(
        'student_dashboard.html',
        events=events,
        vtu_updates=vtu_updates,
        jobs=jobs,
        notifications=notifications  # Pass the combined list
    )

# ... (rest of your code) ...

if __name__ == "__main__":
    with app.app_context():
        # ... (your db.create_all() logic is fine) ...
        db.create_all()
        if not User.query.first():
            db.session.add(User(email="teacher@college.com", password="1234", role="teacher"))
            db.session.add(User(email="student@college.com", password="1234", role="student"))
            db.session.commit()

    # ... (your background thread logic is fine) ...
    import threading
    import time
    
    def notify_upcoming_events():
        # ... (this logic is fine) ...
        while True:
            with app.app_context():
                tomorrow = (datetime.now() + timedelta(days=1)).date()
                today = datetime.now().date()
                events = Event.query.all()
                for event in events:
                    try:
                        event_date = datetime.strptime(event.date, "%Y-%m-%d").date()
                        if event_date == tomorrow:
                            print(f"🔔 Reminder: '{event.title}' is tomorrow!")
                        elif event_date == today:
                            print(f"📢 Today: '{event.title}' is happening!")
                    except Exception as e:
                        print("Date check error:", e)
            time.sleep(86400)

    threading.Thread(target=notify_upcoming_events, daemon=True).start()

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=10000)
    