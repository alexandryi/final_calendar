from flask import Flask
from flask_login import LoginManager

from config import Config
from models import db
from views import register_routes

# Ініціалізація Flask-додатку
app = Flask(__name__)
app.config.from_object(Config)

# Ініціалізація бази даних
db.init_app(app)

# Ініціалізація Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Реєстрація маршрутів з файлу views.py
register_routes(app, login_manager)

# Запуск додатку
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
