from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime, timedelta
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
    servizio = db.Column(db.String(200), nullable=False)  # Permettiamo fino a 200 caratteri per più servizi

# Creazione del database alla prima esecuzione
with app.app_context():
    db.create_all()

# Durate dei servizi
durate_servizi = {
    "Taglio": 30,      # Durata in minuti per Taglio
    "Piega": 45,       # Durata in minuti per Piega
    "Colore": 90,      # Durata in minuti per Colore
    "Trattamento": 45, # Durata in minuti per Trattamento
    "Shampoo": 10      # Durata in minuti per Shampoo
}

# Definizione degli orari di apertura del salone
ORARIO_APERTURA = datetime.strptime("09:00", "%H:%M").time()
ORARIO_CHIUSURA = datetime.strptime("19:00", "%H:%M").time()

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
        
        # Recupera i servizi selezionati
        servizi = request.form.getlist('servizi')
        servizi_str = ", ".join(servizi)

        # Converti la data in un oggetto datetime
        data_obj = datetime.strptime(data, "%Y-%m-%d")

        # 🚨 Controlla se la data selezionata è una domenica
        if data_obj.weekday() == 6:  # 6 = Domenica
            flash("Non è possibile prenotare la domenica. Scegli un altro giorno.", "danger")
            return redirect(url_for('prenotazioni'))
        if data_obj.weekday() == 0:  # 0 = Lunedi
            flash("Non è possibile prenotare il lunedi. Scegli un altro giorno.", "danger")
            return redirect(url_for('prenotazioni'))

        # 🚨 Controlla se l'orario scelto è fuori dagli orari di apertura
        orario_obj = datetime.strptime(orario, "%H:%M").time()
        if orario_obj < ORARIO_APERTURA or orario_obj > ORARIO_CHIUSURA:
            flash("L'orario selezionato è fuori dagli orari di apertura del salone (09:00 - 19:00).", "danger")
            return redirect(url_for('prenotazioni'))

        # Calcola la durata totale dei servizi selezionati
        durata_totale = sum(durate_servizi[servizio] for servizio in servizi)

        # Calcola l'orario di fine della prenotazione
        esistente_inizio = datetime.strptime(orario, '%H:%M')
        esistente_fine = esistente_inizio + timedelta(minutes=durata_totale)

        # Controlla se esistono prenotazioni che si sovrappongono
        prenotazioni_in_giorno = Prenotazione.query.filter_by(data=data).all()
        
        for prenotazione in prenotazioni_in_giorno:
            orario_esistente_inizio = datetime.strptime(prenotazione.orario, '%H:%M')
            durata_servizio_esistente = sum(durate_servizi[servizio] for servizio in prenotazione.servizio.split(', '))
            orario_esistente_fine = orario_esistente_inizio + timedelta(minutes=durata_servizio_esistente)

            if not (esistente_fine <= orario_esistente_inizio or esistente_inizio >= orario_esistente_fine):
                flash('Questo orario è già prenotato per un altro servizio. Scegli un altro orario.', 'danger')
                return redirect(url_for('prenotazioni'))

        # Salva la prenotazione nel database
        nuova_prenotazione = Prenotazione(nome=nome, email=email, data=data, orario=orario, servizio=servizi_str)
        db.session.add(nuova_prenotazione)
        db.session.commit()

        # Invia la mail di conferma
        try:
            msg = Message('Conferma Prenotazione', sender=app.config['MAIL_USERNAME'], recipients=[email, 'lacarbonarafabio18@gmail.com'])
            msg.body = f"Ciao {nome},\n\nHai prenotato un appuntamento per i seguenti servizi: {servizi_str}.\nData: {data}\nOrario: {orario}\n\nGrazie per aver scelto il nostro salone!\n\nSaluti,\nIl team del salone"
            mail.send(msg)
            flash('Prenotazione effettuata con successo! Controlla la tua email.', 'success')
        except Exception as e:
            flash(f"Errore nell'invio dell'email: {e}", 'danger')

        return redirect(url_for('prenotazioni'))

    return render_template('prenotazioni.html')


@app.route('/api/cliente_prenotazioni')
def api_cliente_prenotazioni():
    prenotazioni = Prenotazione.query.all()
    eventi = []
    
    for p in prenotazioni:
        # Calcola la durata totale dei servizi selezionati
        servizi = p.servizio.split(", ")
        durata_totale = sum(durate_servizi[servizio] for servizio in servizi)

        # Calcola l'orario di inizio della prenotazione
        orario_inizio = datetime.strptime(p.orario, '%H:%M')
        orario_fine = orario_inizio + timedelta(minutes=durata_totale)

        # Imposta il titolo come solo l'orario di fine
        titolo_evento = f"{orario_fine.strftime('%H:%M')}"

        # Aggiungi l'evento con orario di inizio e fine
        eventi.append({
            "id": p.id,
            "title": "-" + " " + titolo_evento,  # Mostra solo l'orario di fine
            "start": f"{p.data}T{p.orario}",
            "end": orario_fine.strftime("%Y-%m-%dT%H:%M:%S"),  # Formato ISO per l'ora di fine
            "color": "#FF0000",  # Colore dell'evento
            "textColor": "white"  # Colore del testo
        })
    
    return jsonify(eventi)


@app.route('/api/prenotazioni')
def api_prenotazioni():
    prenotazioni = Prenotazione.query.all()
    eventi = []

    for p in prenotazioni:
        # Calcola la durata totale dei servizi
        servizi = p.servizio.split(', ')
        durata_totale = sum(durate_servizi[servizio] for servizio in servizi)

        # Calcola l'orario di fine
        orario_inizio = datetime.strptime(p.orario, '%H:%M')
        orario_fine = orario_inizio + timedelta(minutes=durata_totale)

        titolo_evento = f"{orario_fine.strftime('%H:%M')}"

        # Aggiungi evento con orario di fine
        evento = {
            "id": p.id,  # Assicurati che l'ID venga passato
            "title": "-" + " " + titolo_evento,  # Titolo con nome e servizio
            "start": p.data + "T" + p.orario,  # Orario di inizio
            "end": orario_fine.strftime("%Y-%m-%dT%H:%M:%S"),  # Orario di fine
            "textColor": "white"  # Colore del testo
        }

        eventi.append(evento)

    return jsonify(eventi)


@app.route('/api/prenotazione/<int:id>')
def api_prenotazione(id):
    prenotazione = Prenotazione.query.get(id)
    if prenotazione:
        # Restituisci i dettagli della prenotazione in formato JSON
        return jsonify({
            'id': prenotazione.id,
            'nome': prenotazione.nome,
            'email': prenotazione.email,
            'data': prenotazione.data,
            'orario': prenotazione.orario,
            'servizio': prenotazione.servizio
        })
    else:
        return jsonify({'error': 'Prenotazione non trovata'}), 404

@app.route('/api/elimina_prenotazione/<int:id>', methods=['DELETE'])
def elimina_prenotazione(id):
    prenotazione = Prenotazione.query.get(id)
    if prenotazione:
        db.session.delete(prenotazione)
        db.session.commit()
        return jsonify({'success': 'Prenotazione eliminata con successo!'}), 200
    else:
        return jsonify({'error': 'Prenotazione non trovata'}), 404

# Pagina admin per vedere tutte le prenotazioni
@app.route('/admin/prenotazioni')
def admin_prenotazioni():
    prenotazioni = Prenotazione.query.all()
    return render_template('admin_prenotazioni.html', prenotazioni=prenotazioni)

if __name__ == '__main__':
    app.run(debug=True)
