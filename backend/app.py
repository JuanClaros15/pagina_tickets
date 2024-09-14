#para manejo de rutas, consultas HTTP y crear aplicacion web
from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
#autenticar los usuarios
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
#conexion con la base de datos
from flask_sqlalchemy import SQLAlchemy
#manejo de las contraseñas
from flask_bcrypt import Bcrypt
#para las instancias 
from main import db, Usuario, Ticket

from werkzeug.security import generate_password_hash, check_password_hash
import logging


logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')  
app.config['SECRET_KEY'] = '5432'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ticketsjuan:6UzxDePH2JRHkcQVpblyLiUkzrNPSiSB@dpg-crj0p8bv2p9s738pq4cg-a.oregon-postgres.render.com/basetickets'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


@app.route('/')
def index():
    return "Hola Mundo!!"

@app.route('/logout',methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/pagina_principal')
@login_required
def pagina_principal():
    return render_template('pagina_principal.html', username=current_user.username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Inicio de sesión exitoso!', 'success')
            return redirect(url_for('pagina_principal'))  
        else:
            flash('Inicio de sesión fallido. Por favor, verifica tu usuario y contraseña.', 'danger')
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])    
def register():
    if request.method == 'POST':
        username = request.form['username']
        mail = request.form['mail']
        password = request.form['password']
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = Usuario(username=username, mail=mail, password=password_hash)
        
        db.session.add(new_user)
        db.session.commit()
        flash('Usuario registrado exitosamente', 'success')
        return redirect(url_for('login'))
    
    return render_template('registro.html')


@app.route('/reset_password', methods=['GET','POST'])
def reset_password():
    if request.method == 'POST':
        username = request.form.get('username')
        mail = request.form.get('mail')
        new_password = request.form.get('new_password')
        user = Usuario.query.filter_by(mail=mail, username=username).first()
        if user:
            user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            db.session.commit()
            flash('Tu contraseña ha sido actualizada con éxito.')
            return redirect(url_for('login'))
        flash('No encontramos un usuario con ese correo y nombre de usuario.')
    return render_template('recuperar_contraseña.html')

@app.route('/tickets', methods=['GET'])
@login_required
def get_tickets():
    if current_user.id_user == 1: 
        tickets = Ticket.query.all()
    else:
        tickets = Ticket.query.filter_by(usuario_id=current_user.id_user).all()
    tickets_list = [{
        'id_ticket': ticket.id_ticket,
        'titulo': ticket.titulo,
        'descripcion': ticket.descripcion,
        'prioridad': ticket.prioridad,
        'estado': ticket.estado,
        'fecha_creacion': ticket.fecha_creacion.strftime('%d/%m/%Y %H:%M:%S'),
        'usuario': ticket.usuario.username,  
        'mail': ticket.usuario.mail,
    } for ticket in tickets]
    return jsonify(tickets_list)

@app.route('/ticket', methods=['POST'])
@login_required
def add_ticket():
    data = request.json
    app.logger.debug(f"Datos recibidos: {data}")
    
    new_ticket = Ticket(
        titulo=data['titulo'],
        descripcion=data['descripcion'],
        prioridad=data['prioridad'],
        estado='en curso',
        usuario_id=current_user.id_user
    )
    db.session.add(new_ticket)
    db.session.commit()
    app.logger.debug("Ticket agregado a la base de datos")

    return jsonify({'message': 'Ticket agregado exitosamente!'}), 201



@app.route('/ticket/<int:ticket_id>/close', methods=['PATCH'])
@login_required
def close_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    ticket.estado = 'finalizado'
    db.session.commit()
    return jsonify({'message': 'Ticket finalizado exitosamente!'})


@app.route('/ticket/<int:ticket_id>', methods=['DELETE'])
@login_required
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({'message': 'Ticket eliminado exitosamente!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

