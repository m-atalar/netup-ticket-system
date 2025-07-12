# setup.py
from app import create_app, db
from app.models import User
from flask_bcrypt import Bcrypt

app = create_app()
app.app_context().push()
bcrypt = Bcrypt()

# Veritabanını oluştur
db.create_all()

# Örnek kullanıcılar
admin = User(
    username="admin",
    password_hash=bcrypt.generate_password_hash("admin123").decode('utf-8'),
    role="admin",
    email="admin@example.com"
)

agent = User(
    username="agent",
    password_hash=bcrypt.generate_password_hash("agent123").decode('utf-8'),
    role="agent",
    email="agent@example.com"
)

# Veritabanına ekle
db.session.add(admin)
db.session.add(agent)
db.session.commit()

print("✅ Admin ve Agent kullanıcıları başarıyla oluşturuldu.")
