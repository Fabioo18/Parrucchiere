from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import os

app = Flask(__name__)

# Configurazione database SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prenotazioni.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

db = SQLAlchemy(app)

# Configurazione email (Gmail)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'lacarbonarafabio18@gmail.com'  # Cambia con il tuo indirizzo Gmail
app.config['MAIL_PASSWORD'] = 'teag qlhq neuo sfsn'  # Password generata per le app

mail = Mail(app)

# Modello database per le prenotazioni
class Prenotazione(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    data = db.Column(db.String(50), nullable=False)
    orario = db.Column(db.String(50), nullable=False)
    servizio = db.Column(db.String(100), nullable=False)

# Creazione del database alla prima esecuzione
with app.app_context():
    db.create_all()

# Homepage
@app.route('/')
def index():
    return render_template('index.html')

# Pagina prenotazioni
@app.route('/prenotazioni', methods=['GET', 'POST'])
def prenotazioni():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        data = request.form['data']
        orario = request.form['orario']
        servizio = request.form['servizio']

        # Controllo se l'orario è già occupato
        prenotazione_esistente = Prenotazione.query.filter_by(data=data, orario=orario).first()
        if prenotazione_esistente:
            flash('Questo orario è già prenotato. Scegli un altro orario.', 'danger')
            return redirect(url_for('prenotazioni'))

        # Salva la prenotazione nel database
        nuova_prenotazione = Prenotazione(nome=nome, email=email, data=data, orario=orario, servizio=servizio)
        db.session.add(nuova_prenotazione)
        db.session.commit()

        # Invia la mail di conferma
        try:
            msg = Message('Conferma Prenotazione', sender=app.config['MAIL_USERNAME'], recipients=[email, 'lacarbonarafabio18@gmail.com'])
            msg.body = f"Ciao {nome},\n\nHai prenotato un appuntamento per il servizio: {servizio}.\nData: {data}\nOrario: {orario}\n\nGrazie per aver scelto il nostro salone!\n\nSaluti,\nIl team del salone"
            mail.send(msg)
            flash('Prenotazione effettuata con successo! Controlla la tua email.', 'success')
        except Exception as e:
            flash(f"Errore nell'invio dell'email: {e}", 'danger')

        return redirect(url_for('prenotazioni'))

    return render_template('prenotazioni.html')

# Pagina admin per vedere tutte le prenotazioni
@app.route('/admin/prenotazioni')
def admin_prenotazioni():
    prenotazioni = Prenotazione.query.all()
    return render_template('admin_prenotazioni.html', prenotazioni=prenotazioni)

if __name__ == '__main__':
    app.run(debug=True)