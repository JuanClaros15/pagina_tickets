from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id_user = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    mail = db.Column(db.String(150), unique=True, nullable=False)

    # Relación con tickets
    tickets = db.relationship('Ticket', backref='usuario', lazy=True)

    def __repr__(self):
        return f"Usuario('{self.username}', '{self.mail}')"

    def get_id(self):
        return str(self.id_user)

class Ticket(db.Model):
    __tablename__ = 'tickets'
    id_ticket = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    prioridad = db.Column(db.String(10), nullable=False)
    estado = db.Column(db.String(10), default='en curso', nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_user'), nullable=False)

    def __repr__(self):
        return f"Ticket('{self.titulo}', '{self.estado}')"
