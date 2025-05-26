from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password=generate_password_hash('admin123'), role='admin')
        coord = User(username='coordenador', password=generate_password_hash('coord123'), role='coordenador')
        prof = User(username='professor', password=generate_password_hash('prof123'), role='professor')
        
        db.session.add_all([admin, coord, prof])
        db.session.commit()
        print("✅ Usuários de teste criados com sucesso!")
    else:
        print("⚠️ Usuários já existem.")

