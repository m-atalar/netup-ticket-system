from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from app.models import db, User

migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Giriş yapılmadıysa yönlendirilecek sayfa

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprintleri ekle
    from .routes import tickets
    from .routes import auth
    app.register_blueprint(tickets.bp)
    app.register_blueprint(auth.bp)

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    return app


