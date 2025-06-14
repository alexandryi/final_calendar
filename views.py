from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import calendar

from models import db, User, Event

HOLIDAYS = {
    "2025-01-01": "New Year",
    "2025-12-25": "Christmas"
}

def register_routes(app, login_manager):

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    @login_required
    def index():
        year = datetime.now().year
        user_events = Event.query.filter_by(user_id=current_user.id).all()
        global_events = Event.query.filter_by(user_id=None).all()
        all_events = user_events + global_events

        events_by_date = {}
        for event in all_events:
            key = event.date.strftime('%Y-%m-%d')
            events_by_date.setdefault(key, []).append({"id": event.id, "note": event.note})

        months_data = []
        today_str = datetime.now().strftime("%Y-%m-%d")

        for month in range(1, 13):
            month_days = []
            cal = calendar.Calendar().monthdayscalendar(year, month)
            for week in cal:
                week_days = []
                for day in week:
                    if day == 0:
                        week_days.append({'day': '', 'date_str': '', 'event': None, 'holiday': None, 'is_today': False})
                    else:
                        full_date = f"{year}-{month:02d}-{day:02d}"
                        week_days.append({
                            'day': day,
                            'date_str': full_date,
                            'event': events_by_date.get(full_date),
                            'holiday': HOLIDAYS.get(full_date),
                            'is_today': full_date == today_str
                        })
                month_days.append(week_days)
            months_data.append({
                'name': calendar.month_name[month],
                'weeks': month_days
            })

        return render_template("calendar.html", months=months_data, year=year, today=today_str)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if User.query.filter_by(username=username).first():
                flash('Username already exists')
                return redirect(url_for('register'))
            new_user = User(username=username, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created! Please log in.')
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('index'))
            flash('Invalid credentials')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/add_event', methods=['POST'])
    @login_required
    def add_event():
        date_str = request.form['date']
        note = request.form['note']
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        event = Event(date=date_obj, note=note, user_id=current_user.id)
        db.session.add(event)
        db.session.commit()
        return redirect(url_for('index'))

    @app.route('/edit_event', methods=['POST'])
    @login_required
    def edit_event():
        event_id = request.form['id']
        new_note = request.form['note']
        event = Event.query.get(event_id)
        if event and event.user_id == current_user.id:
            event.note = new_note
            db.session.commit()
        return redirect(url_for('index'))

    @app.route('/delete_event/<int:event_id>', methods=['POST'])
    @login_required
    def delete_event(event_id):
        event = Event.query.get(event_id)
        if event and event.user_id == current_user.id:
            db.session.delete(event)
            db.session.commit()
        return redirect(url_for('index'))
