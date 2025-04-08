from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.facebook import make_facebook_blueprint
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from flask_migrate import Migrate
load_dotenv(dotenv_path='file.env')
import requests
import os

app = Flask(__name__)

# Configurazione database SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prenotazioni.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'connect_args': {'timeout': 30}}
app.secret_key = 'supersecretkey'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Dopo aver inizializzato `db`
migrate = Migrate(app, db)

# Configurazione Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Configurazione email (Gmail)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'lacarbonarafabio18@gmail.com'  # Cambia con il tuo indirizzo Gmail
app.config['MAIL_PASSWORD'] = 'teag qlhq neuo sfsn'  # Password generata per le app

mail = Mail(app)

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Consenti HTTP per OAuth in locale


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# Configurazione OAuth per Google e Facebook
google_bp = make_google_blueprint(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    scope=[
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid"
    ],
    redirect_to="google_login"
)
facebook_bp = make_facebook_blueprint(client_id="FACEBOOK_CLIENT_ID", client_secret="FACEBOOK_CLIENT_SECRET", redirect_to="facebook_login")
app.register_blueprint(google_bp, url_prefix="/login")
app.register_blueprint(facebook_bp, url_prefix="/login")

# Modello database per gli utenti
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=True)
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="cliente")  # "cliente", "parrucchiere", "operatore"
    operatore_id = db.Column(db.Integer, db.ForeignKey('operatore.id'), nullable=True)  # Associa un operatore

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))  # Assicurati che carichi correttamente l'utente

# Modello database per gli operatori
class Operatore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    prenotazioni = db.relationship('Prenotazione', backref='operatore', lazy=True)

# Modello database per le prenotazioni
class Prenotazione(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    data = db.Column(db.String(50), nullable=False)
    orario = db.Column(db.String(50), nullable=False)
    servizio = db.Column(db.String(200), nullable=False)  # Permettiamo fino a 200 caratteri per più servizi
    operatore_id = db.Column(db.Integer, db.ForeignKey('operatore.id'), nullable=False)

# Creazione del database alla prima esecuzione
with app.app_context():
    db.create_all()

# with app.app_context():
#     user = User.query.filter_by(email='admin@salone.it').first()
#     print(f"Ruolo nel database: {user.role}")

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
    if current_user.is_authenticated:
        print(f"Utente autenticato: {current_user.name}, Ruolo: {current_user.role}")
    return render_template('index.html', user=current_user)

# Rotta per la registrazione
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')

            # Controlla se tutti i campi sono compilati
            if not name or not email or not password:
                flash('Tutti i campi sono obbligatori.', 'danger')
                return redirect(url_for('register'))

            # Controlla se l'email è già registrata
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email già registrata.', 'danger')
                return redirect(url_for('register'))

            # Genera l'hash della password
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            # Crea un nuovo utente con ruolo predefinito "cliente"
            new_user = User(name=name, email=email, password=hashed_password, role="cliente")
            db.session.add(new_user)
            db.session.commit()

            flash('Registrazione completata! Ora puoi accedere.', 'success')
            return redirect(url_for('login'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Errore durante la registrazione: {str(e)}", 'danger')
            return redirect(url_for('register'))
        finally:
            db.session.close()

    return render_template('register.html')

# Rotta per il login con mail e password
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and user.password and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash(f'Accesso effettuato con successo! <br> <br> Ciao, {user.name}.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Credenziali non valide. Controlla email e password.', 'danger')

    return render_template('login.html')

# Rotta per il logout
@app.route('/logout')
@login_required
def logout():
    # Logout dell'utente da Flask
    logout_user()

    # Logout da Google (se è stato effettuato l'accesso)
    if google.authorized:
        # Ottieni il token di accesso dalla sessione
        token = google_bp.session.token.get("access_token")
        if token:
            # Effettua una richiesta all'endpoint di revoca di Google
            revoke_url = "https://oauth2.googleapis.com/revoke"
            params = {"token": token}
            headers = {"content-type": "application/x-www-form-urlencoded"}
            response = requests.post(revoke_url, params=params, headers=headers)

            # Controlla se la revoca è andata a buon fine
            if response.status_code == 200:
                flash('Logout effettuato.', 'success')
            else:
                flash("")

        # Cancella eventuali cookie OAuth
        del google_bp.session.token

    # Reindirizza alla homepage dopo il logout
    flash('Logout effettuato con successo.', 'success')
    return redirect(url_for('index'))



@app.route('/google_login')
def google_login():
    # Forza sempre la selezione dell'account, anche se l'utente è già connesso
    if not google.authorized:
        # Aggiungi il parametro `prompt=select_account` per forzare la selezione dell'account
        return redirect(url_for("google.login") + "?prompt=select_account")

    try:
        # Richiesta delle informazioni dell'utente da Google
        resp = google.get("/oauth2/v2/userinfo")
        if not resp.ok:
            flash("Errore durante l'accesso con Google.", "danger")
            return redirect(url_for("login"))

        # Ottieni le informazioni dell'utente
        user_info = resp.json()
        email = user_info.get("email")
        name = user_info.get("name", "Utente")

        if not email:
            flash("Errore durante l'accesso con Google: l'email non è disponibile.", "danger")
            return redirect(url_for("login"))

        # Verifica se l'utente esiste nel database
        user = User.query.filter_by(email=email).first()
        if not user:
            # Se non esiste, crealo
            user = User(email=email, name=name, role="cliente")
            db.session.add(user)
            db.session.commit()

        # Effettua il login dell'utente
        login_user(user)
        flash(f"Accesso effettuato con successo!<br><br>Ciao, {user.name}.", "success")
        return redirect(url_for('index'))

    except Exception as e:
        flash(f"Errore durante l'accesso con Google: {str(e)}", "danger")
        return redirect(url_for("login"))

# # Rotta per il login con Facebook
# @app.route('/facebook_login')
# def facebook_login():
#     if not facebook.authorized:
#         return redirect(url_for("facebook.login"))
#     resp = facebook.get("/me?fields=id,name,email")
#     user_info = resp.json()
#     email = user_info["email"]
#     name = user_info["name"]

#     user = User.query.filter_by(email=email).first()
#     if not user:
#         user = User(email=email, name=name, role="cliente")
#         db.session.add(user)
#         db.session.commit()

#     login_user(user)
#     flash('Accesso effettuato con Facebook!', 'success')
#     return redirect(url_for('index'))

# Pagina prenotazioni
@app.route('/prenotazioni', methods=['GET', 'POST'])
def prenotazioni():
    operatore_id = request.args.get('operatore_id') or request.form.get('operatore_id')
    if not operatore_id:
        flash("Seleziona un operatore per visualizzare il calendario.", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        nome = request.form.get('nome') or (current_user.name if current_user.is_authenticated else None)
        email = request.form.get('email') or (current_user.email if current_user.is_authenticated else None)
        data = request.form['data']
        orario = request.form['orario']
        
        # Controlla se nome ed email sono forniti
        if not nome or not email:
            flash("Nome ed email sono obbligatori per effettuare una prenotazione.", "danger")
            return redirect(url_for('prenotazioni', operatore_id=operatore_id))

        # Recupera i servizi selezionati
        servizi = request.form.getlist('servizi')
        servizi_str = ", ".join(servizi)

        # Converti la data in un oggetto datetime
        data_obj = datetime.strptime(data, "%Y-%m-%d")

        # Recupera la data odierna
        data_odierna = datetime.today()

        # Controlla se la data selezionata è una domenica o lunedì
        if data_obj.weekday() in {6, 0}:  # 6 = Domenica, 0 = Lunedì
            flash("Non è possibile prenotare la domenica o il lunedì. Scegli un altro giorno.", "danger")
            return redirect(url_for('prenotazioni', operatore_id=operatore_id))

        # Controlla se la data selezionata è prima della data odierna
        if data_obj < data_odierna:
            flash("Non è possibile prenotare una data passata. Scegli una data a partire da oggi.", "danger")
            return redirect(url_for('prenotazioni', operatore_id=operatore_id))

        # Controlla se l'orario scelto è fuori dagli orari di apertura
        orario_obj = datetime.strptime(orario, "%H:%M").time()
        if orario_obj < ORARIO_APERTURA or orario_obj > ORARIO_CHIUSURA:
            flash("L'orario selezionato è fuori dagli orari di apertura del salone (09:00 - 19:00).", "danger")
            return redirect(url_for('prenotazioni', operatore_id=operatore_id))

        # Calcola la durata totale dei servizi selezionati
        durata_totale = sum(durate_servizi[servizio] for servizio in servizi)

        # Calcola l'orario di fine della prenotazione
        esistente_inizio = datetime.strptime(orario, '%H:%M')
        esistente_fine = esistente_inizio + timedelta(minutes=durata_totale)

        # Controlla se esistono prenotazioni che si sovrappongono per l'operatore selezionato
        prenotazioni_in_giorno = Prenotazione.query.filter_by(data=data, operatore_id=operatore_id).all()
        
        for prenotazione in prenotazioni_in_giorno:
            orario_esistente_inizio = datetime.strptime(prenotazione.orario, '%H:%M')
            durata_servizio_esistente = sum(durate_servizi[servizio] for servizio in prenotazione.servizio.split(', '))
            orario_esistente_fine = orario_esistente_inizio + timedelta(minutes=durata_servizio_esistente)

            if not (esistente_fine <= orario_esistente_inizio or esistente_inizio >= orario_esistente_fine):
                flash('Questo orario è già prenotato per un altro servizio. Scegli un altro orario.', 'danger')
                return redirect(url_for('prenotazioni', operatore_id=operatore_id))

        # Salva la prenotazione nel database
        nuova_prenotazione = Prenotazione(nome=nome, email=email, data=data, orario=orario, servizio=servizi_str, operatore_id=operatore_id)
        db.session.add(nuova_prenotazione)
        db.session.commit()

        # Invia la mail di conferma
        try:
            operatore = Operatore.query.get(operatore_id)
            nome_operatore = operatore.nome if operatore else "Operatore non specificato"
            msg = Message('Conferma Prenotazione', sender=app.config['MAIL_USERNAME'], recipients=[email, 'lacarbonarafabio18@gmail.com'])
            msg.body = f"Ciao {nome},\n\nHai prenotato un appuntamento per i seguenti servizi: {servizi_str}.\nData: {data}\nOrario: {orario}\nOperatore: {nome_operatore}\n\nGrazie per aver scelto il nostro salone!\n\nSaluti,\nIl team del salone"
            mail.send(msg)
            flash('Prenotazione effettuata con successo! Controlla la tua email.', 'success')
        except Exception as e:
            flash(f"Errore nell'invio dell'email: {e}", 'danger')

        return redirect(url_for('prenotazioni', operatore_id=operatore_id))

    # Precompila i campi se l'utente è autenticato
    nome = current_user.name if current_user.is_authenticated else ""
    email = current_user.email if current_user.is_authenticated else ""

    return render_template('prenotazioni.html', nome=nome, email=email, operatore_id=operatore_id)

# @app.route('/api/cliente_prenotazioni')
# def api_cliente_prenotazioni():
#     prenotazioni = Prenotazione.query.all()
#     eventi = []
    
#     # Set di giorni non prenotabili
#     giorni_non_prenotabili = {6, 0}  # Domenica (6) e Lunedì (0)

#     for p in prenotazioni:
#         # Calcola la durata totale dei servizi selezionati
#         servizi = p.servizio.split(", ")
#         durata_totale = sum(durate_servizi[servizio] for servizio in servizi)

#         # Calcola l'orario di inizio della prenotazione
#         orario_inizio = datetime.strptime(p.orario, '%H:%M')
#         orario_fine = orario_inizio + timedelta(minutes=durata_totale)

#         titolo_evento = f"{orario_fine.strftime('%H:%M')}"

#         # Aggiungi evento con orario di fine
#         evento = {
#             "id": p.id,  # Assicurati che l'ID venga passato
#             "title": "-" + " " + titolo_evento,  # Titolo con nome e servizio
#             "start": p.data + "T" + p.orario,  # Orario di inizio
#             "end": orario_fine.strftime("%Y-%m-%dT%H:%M:%S"),  # Orario di fine
#             "textColor": "white"  # Colore del testo
#         }

#         eventi.append(evento)

#     # Aggiungi giorni non prenotabili
#     prenotazioni_per_data = {}
#     for p in prenotazioni:
#         if p.data not in prenotazioni_per_data:
#             prenotazioni_per_data[p.data] = []

#     for data in prenotazioni_per_data:
#         if datetime.strptime(data, "%Y-%m-%d").weekday() in giorni_non_prenotabili:
#             eventi.append({
#                 "id": "non_prenotabile_" + data,
#                 "title": "Giorno non prenotabile",
#                 "start": f"{data}T00:00:00",
#                 "end": f"{data}T23:59:59",
#                 "color": "#FF0000",  # Colore rosso
#                 "textColor": "white"
#             })
    
#     return jsonify(eventi)

@app.route('/api/cliente_prenotazioni/<int:operatore_id>')
def api_cliente_prenotazioni(operatore_id):
    prenotazioni = Prenotazione.query.filter_by(operatore_id=operatore_id).all()
    eventi = []

    for p in prenotazioni:
        # Calcola la durata totale dei servizi selezionati
        servizi = p.servizio.split(", ")
        durata_totale = sum(durate_servizi[servizio] for servizio in servizi)

        # Calcola l'orario di fine
        orario_inizio = datetime.strptime(p.orario, '%H:%M')
        orario_fine = orario_inizio + timedelta(minutes=durata_totale)

        titolo_evento = f"{orario_fine.strftime('%H:%M')}"

        evento = {
            "id": p.id,  # Assicurati che l'ID venga passato
            "title": "-" + " " + titolo_evento,  # Titolo con nome e servizio
            "start": p.data + "T" + p.orario,  # Orario di inizio
            "end": orario_fine.strftime("%Y-%m-%dT%H:%M:%S"),  # Orario di fine
            "textColor": "white"  # Colore del testo
        }

        eventi.append(evento)

    return jsonify(eventi)

@app.route('/api/operatori', methods=['GET'])
def get_operatori():
    operatori = Operatore.query.all()
    print("Operatori trovati:", operatori)  # Log per verificare i dati
    return jsonify([{'id': operatore.id, 'nome': operatore.nome} for operatore in operatori])


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

@app.route('/api/orari_disponibili_operatore/<int:operatore_id>/<data>', methods=['GET'])
def orari_disponibili_operatore(operatore_id, data):
    prenotazioni = Prenotazione.query.filter_by(data=data, operatore_id=operatore_id).all()
    orari_prenotati = [(datetime.strptime(p.orario, '%H:%M').time(),
                        (datetime.strptime(p.orario, '%H:%M') + timedelta(minutes=sum(durate_servizi[s] for s in p.servizio.split(', ')))).time())
                       for p in prenotazioni]

    orari_possibili = []
    ora_corrente = datetime.strptime("09:00", "%H:%M")
    ora_fine = datetime.strptime("19:00", "%H:%M")

    while ora_corrente.time() < ora_fine.time():
        prossimo_slot = (ora_corrente + timedelta(minutes=30)).time()
        disponibile = all(prossimo_slot <= inizio or ora_corrente.time() >= fine for inizio, fine in orari_prenotati)
        if disponibile:
            orari_possibili.append(ora_corrente.strftime("%H:%M"))
        ora_corrente += timedelta(minutes=30)

    return jsonify(orari_possibili)

@app.route('/api/prenotazioni')
@login_required
def api_prenotazioni():
    if current_user.role == 'parrucchiere':
        # Il parrucchiere vede tutte le prenotazioni
        prenotazioni = Prenotazione.query.all()
    elif current_user.role == 'operatore':
        # L'operatore vede solo le sue prenotazioni
        prenotazioni = Prenotazione.query.filter_by(operatore_id=current_user.operatore_id).all()
    else:
        return jsonify({'error': 'Non autorizzato'}), 403

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
            'servizio': prenotazione.servizio,
            'operatore_id': prenotazione.operatore_id  # Aggiungi l'operatore
        })
    else:
        return jsonify({'error': 'Prenotazione non trovata'}), 404
    
@app.route('/api/modifica_prenotazione/<int:id>', methods=['PUT'])
@login_required
def modifica_prenotazione(id):
    prenotazione = Prenotazione.query.get(id)
    if not prenotazione:
        return jsonify({'error': 'Prenotazione non trovata'}), 404

    # Controlla se l'utente è autorizzato a modificare la prenotazione
    if current_user.role == 'operatore' and prenotazione.operatore_id != current_user.operatore_id:
        return jsonify({'error': 'Non sei autorizzato a modificare questa prenotazione'}), 403

    data = request.json
    nuova_data = data.get('data', prenotazione.data)
    nuovo_orario = data.get('orario', prenotazione.orario)
    nuovo_nome = data.get('nome', prenotazione.nome)
    nuova_email = data.get('email', prenotazione.email)
    nuovo_servizio = data.get('servizio', prenotazione.servizio)

    # Gli operatori non possono modificare il campo "Operatore"
    if current_user.role == 'parrucchiere':
        nuovo_operatore_id = data.get('operatore_id', prenotazione.operatore_id)
    else:
        nuovo_operatore_id = prenotazione.operatore_id

    # Verifica che la nuova data non sia prima di oggi
    today = datetime.today().date()
    nuova_data_obj = datetime.strptime(nuova_data, "%Y-%m-%d").date()

    if nuova_data_obj < today:
        return jsonify({'error': 'Non è possibile prenotare per una data passata. Scegli una data a partire da oggi.'}), 400

    # Set di giorni non prenotabili (Domenica e Lunedì)
    giorni_non_prenotabili = {6, 0}  # Domenica (6) e Lunedì (0)

    if nuova_data_obj.weekday() in giorni_non_prenotabili:
        return jsonify({'error': 'Non è possibile prenotare per domenica o lunedì.'}), 400

    try:
        orario_prenotazione = datetime.strptime(nuovo_orario, "%H:%M").time()
        if orario_prenotazione < ORARIO_APERTURA or orario_prenotazione > ORARIO_CHIUSURA:
            return jsonify({'error': f'Orario non valido! Il salone è aperto dalle {ORARIO_APERTURA.strftime("%H:%M")} alle {ORARIO_CHIUSURA.strftime("%H:%M")}'}), 400
    except ValueError:
        return jsonify({'error': 'Formato orario non valido. Usa HH:MM'}), 400

    # Controllo se l'orario è già occupato
    prenotazione_esistente = Prenotazione.query.filter(
        Prenotazione.data == nuova_data,
        Prenotazione.orario == nuovo_orario,
        Prenotazione.operatore_id == nuovo_operatore_id,
        Prenotazione.id != id
    ).first()

    if prenotazione_esistente:
        return jsonify({'error': 'Orario già prenotato per questo operatore. Scegli un altro orario.'}), 400

    # Aggiorna i dettagli della prenotazione
    prenotazione.nome = nuovo_nome
    prenotazione.email = nuova_email
    prenotazione.data = nuova_data
    prenotazione.orario = nuovo_orario
    prenotazione.servizio = nuovo_servizio
    prenotazione.operatore_id = nuovo_operatore_id

    db.session.commit()

    # Invia l'email con i dettagli aggiornati
    try:
        operatore = Operatore.query.get(nuovo_operatore_id)
        nome_operatore = operatore.nome if operatore else "Operatore non specificato"
        msg = Message(
            "Modifica Prenotazione - Salone di Bellezza",
            sender=app.config['MAIL_USERNAME'],
            recipients=[nuova_email]
        )
        msg.body = f"""
        Ciao {nuovo_nome},

        La tua prenotazione è stata modificata con successo. Ecco i dettagli aggiornati:

        - Data: {nuova_data}
        - Orario: {nuovo_orario}
        - Servizio: {nuovo_servizio}
        - Operatore: {nome_operatore}

        Grazie per aver scelto il nostro salone!

        Saluti,
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
@login_required
def admin_prenotazioni():
    if current_user.role == 'parrucchiere':
        # L'admin globale vede tutte le prenotazioni
        prenotazioni = Prenotazione.query.all()
        operatori = Operatore.query.all()  # Recupera tutti gli operatori
    elif current_user.role == 'operatore':
        # L'operatore vede solo le sue prenotazioni
        prenotazioni = Prenotazione.query.filter_by(operatore_id=current_user.operatore_id).all()
        operatori = None  # Gli operatori non devono vedere la lista di altri operatori
    else:
        flash('Accesso negato. Solo gli admin possono accedere a questa pagina.', 'danger')
        return redirect(url_for('index'))

    return render_template('admin_prenotazioni.html', prenotazioni=prenotazioni, operatori=operatori, user_role=current_user.role)


if __name__ == '__main__':
    app.run(debug=True)

