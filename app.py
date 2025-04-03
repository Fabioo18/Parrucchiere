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

        # Recupera la data odierna
        data_odierna = datetime.today()

        # 🚨 Controlla se la data selezionata è una domenica
        if data_obj.weekday() == 6:  # 6 = Domenica
            flash("Non è possibile prenotare la domenica. Scegli un altro giorno.", "danger")
            return redirect(url_for('prenotazioni'))
        if data_obj.weekday() == 0:  # 0 = Lunedi
            flash("Non è possibile prenotare il lunedi. Scegli un altro giorno.", "danger")
            return redirect(url_for('prenotazioni'))

        # 🚨 Controlla se la data selezionata è prima della data odierna
        if data_obj < data_odierna:
            flash("Non è possibile prenotare una data passata. Scegli una data a partire da oggi.", "danger")
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
    
    # Set di giorni non prenotabili
    giorni_non_prenotabili = {6, 0}  # Domenica (6) e Lunedì (0)

    for p in prenotazioni:
        # Calcola la durata totale dei servizi selezionati
        servizi = p.servizio.split(", ")
        durata_totale = sum(durate_servizi[servizio] for servizio in servizi)

        # Calcola l'orario di inizio della prenotazione
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

    # Aggiungi giorni non prenotabili
    prenotazioni_per_data = {}
    for p in prenotazioni:
        if p.data not in prenotazioni_per_data:
            prenotazioni_per_data[p.data] = []

    for data in prenotazioni_per_data:
        if datetime.strptime(data, "%Y-%m-%d").weekday() in giorni_non_prenotabili:
            eventi.append({
                "id": "non_prenotabile_" + data,
                "title": "Giorno non prenotabile",
                "start": f"{data}T00:00:00",
                "end": f"{data}T23:59:59",
                "color": "#FF0000",  # Colore rosso
                "textColor": "white"
            })
    
    return jsonify(eventi)


@app.route('/api/orari_disponibili/<data>', methods=['GET'])
def orari_disponibili(data):
    # Orari di apertura del salone
    orari_possibili = []
    ora_corrente = datetime.strptime("09:00", "%H:%M")  # Inizio giornata lavorativa
    ora_fine = datetime.strptime("19:00", "%H:%M")  # Fine giornata lavorativa

    # Recupera le prenotazioni esistenti per quella data
    prenotazioni = Prenotazione.query.filter_by(data=data).all()
    orari_prenotati = []

    # Genera gli orari prenotati
    for p in prenotazioni:
        orario_inizio = datetime.strptime(p.orario, '%H:%M')
        durata = sum(durate_servizi[servizio] for servizio in p.servizio.split(", "))
        orario_fine = orario_inizio + timedelta(minutes=durata)

        orari_prenotati.append((orario_inizio.time(), orario_fine.time()))

    # Genera gli slot di 30 minuti tra gli orari di apertura e chiusura
    while ora_corrente.time() < ora_fine.time():
        prossimo_slot = (ora_corrente + timedelta(minutes=30)).time()
        disponibile = True

        # Controlla se l'orario si sovrappone con una prenotazione esistente
        for inizio, fine in orari_prenotati:
            if not (prossimo_slot <= inizio or ora_corrente.time() >= fine):
                disponibile = False
                break

        if disponibile:
            orari_possibili.append(ora_corrente.strftime("%H:%M"))

        ora_corrente += timedelta(minutes=30)

    return jsonify(orari_possibili)

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
    
@app.route('/api/modifica_prenotazione/<int:id>', methods=['PUT'])
def modifica_prenotazione(id):
    prenotazione = Prenotazione.query.get(id)
    if not prenotazione:
        return jsonify({'error': 'Prenotazione non trovata'}), 404

    data = request.json
    nuova_data = data.get('data', prenotazione.data)

    # Verifica che la nuova data non sia prima di oggi
    today = datetime.today().date()  # Ottieni la data odierna
    nuova_data_obj = datetime.strptime(nuova_data, "%Y-%m-%d").date()

    if nuova_data_obj < today:
        return jsonify({'error': 'Non è possibile prenotare per una data passata. Scegli una data a partire da oggi.'}), 400

    # Set di giorni non prenotabili (Domenica e Lunedì)
    giorni_non_prenotabili = {6, 0}  # Domenica (6) e Lunedì (0)

    # Verifica se la nuova data è domenica o lunedì
    if nuova_data_obj.weekday() in giorni_non_prenotabili:
        return jsonify({'error': 'Non è possibile prenotare per domenica o lunedì.'}), 400

    nuovo_orario = data.get('orario', prenotazione.orario)
    nuovo_nome = data.get('nome', prenotazione.nome)
    nuova_email = data.get('email', prenotazione.email)
    nuovo_servizio = data.get('servizio', prenotazione.servizio)

    try:
        # Convertiamo l'orario in formato time() per il confronto
        orario_prenotazione = datetime.strptime(nuovo_orario, "%H:%M").time()
        
        # Controllo se l'orario è dentro l'orario di apertura del salone
        if orario_prenotazione < ORARIO_APERTURA or orario_prenotazione > ORARIO_CHIUSURA:
            return jsonify({'error': f'Orario non valido! Il salone è aperto dalle {ORARIO_APERTURA.strftime("%H:%M")} alle {ORARIO_CHIUSURA.strftime("%H:%M")}'}), 400
    except ValueError:
        return jsonify({'error': 'Formato orario non valido. Usa HH:MM'}), 400

    # Controllo se l'orario è già occupato
    prenotazione_esistente = Prenotazione.query.filter(
        Prenotazione.data == nuova_data,
        Prenotazione.orario == nuovo_orario,
        Prenotazione.id != id
    ).first()

    if prenotazione_esistente:
        return jsonify({'error': 'Orario già prenotato. Scegli un altro orario.'}), 400

    # **Salvataggio delle vecchie informazioni per l'email**
    vecchia_prenotazione = {
        "Nome": prenotazione.nome,
        "Email": prenotazione.email,
        "Data": prenotazione.data,
        "Orario": prenotazione.orario,
        "Servizio": prenotazione.servizio
    }

    # Se tutto è valido, aggiorna la prenotazione
    prenotazione.nome = nuovo_nome
    prenotazione.email = nuova_email
    prenotazione.data = nuova_data
    prenotazione.orario = nuovo_orario
    prenotazione.servizio = nuovo_servizio

    db.session.commit()

    # **Invio email di conferma modifica**
    try:
        msg = Message(
            subject="Modifica Prenotazione - Salone di Bellezza",
            sender="tuamail@example.com",
            recipients=[prenotazione.email]
        )
        msg.body = f"""
        Ciao {prenotazione.nome},

        La tua prenotazione è stata modificata con successo.

        **Dettagli della vecchia prenotazione:**
        - Nome: {vecchia_prenotazione["Nome"]}
        - Email: {vecchia_prenotazione["Email"]}
        - Data: {vecchia_prenotazione["Data"]}
        - Orario: {vecchia_prenotazione["Orario"]}
        - Servizio: {vecchia_prenotazione["Servizio"]}

        **Nuovi dettagli della prenotazione:**
        - Nome: {prenotazione.nome}
        - Email: {prenotazione.email}
        - Data: {prenotazione.data}
        - Orario: {prenotazione.orario}
        - Servizio: {prenotazione.servizio}

        Se non hai richiesto questa modifica, contattaci subito!

        Grazie,
        Il Team del Salone di Bellezza
        """
        mail.send(msg)
    except Exception as e:
        return jsonify({'success': 'Prenotazione modificata, ma errore nell’invio dell’email.', 'error': str(e)}), 500

    return jsonify({'success': 'Prenotazione modificata con successo! Email inviata.'})


@app.route('/api/elimina_prenotazione/<int:id>', methods=['DELETE'])
def elimina_prenotazione(id):
    prenotazione = Prenotazione.query.get(id)
    if prenotazione:
        # Salvataggio dei dati per l'email
        nome_cliente = prenotazione.nome
        email_cliente = prenotazione.email
        data_prenotazione = prenotazione.data
        orario_prenotazione = prenotazione.orario
        servizio_prenotazione = prenotazione.servizio

        # Rimuove la prenotazione dal database
        db.session.delete(prenotazione)
        db.session.commit()

        # Invia l'email di notifica
        try:
            msg = Message(
                "Cancellazione Prenotazione - Salone di Bellezza",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email_cliente]
            )
            msg.body = f"""
            Ciao {nome_cliente},

            La tua prenotazione per i seguenti servizi è stata cancellata:

            - Data: {data_prenotazione}
            - Orario: {orario_prenotazione}
            - Servizio: {servizio_prenotazione}

            Se non hai richiesto questa cancellazione, contattaci immediatamente.

            Grazie,
            Il Team del Salone di Bellezza
            """
            mail.send(msg)
        except Exception as e:
            return jsonify({'success': 'Prenotazione eliminata, ma errore nell’invio dell’email.', 'error': str(e)}), 500

        return jsonify({'success': 'Prenotazione eliminata con successo! Email inviata.'}), 200
    else:
        return jsonify({'error': 'Prenotazione non trovata'}), 404


# Pagina admin per vedere tutte le prenotazioni
@app.route('/admin/prenotazioni')
def admin_prenotazioni():
    prenotazioni = Prenotazione.query.all()
    return render_template('admin_prenotazioni.html', prenotazioni=prenotazioni)

if __name__ == '__main__':
    app.run(debug=True)
