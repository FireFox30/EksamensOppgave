from flask import Flask, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'bytt-meg-ut'

DATABASE = 'helpdesk.db'


# ─── Database-hjelper ─────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # gjør at vi kan bruke kolonnenavn
    return conn


def init_db():
    """Opprett tabeller og legg til testbruker hvis databasen er tom."""
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            email         TEXT NOT NULL UNIQUE,
            role          TEXT NOT NULL DEFAULT 'bruker',
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS tickets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            title       TEXT NOT NULL,
            description TEXT NOT NULL,
            category    TEXT NOT NULL DEFAULT 'annet',
            status      TEXT NOT NULL DEFAULT 'åpen',
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')

    # Legg til admin-bruker hvis ingen brukere finnes
    existing = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
    if not existing:
        conn.execute(
            "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
            ('admin', 'admin@firma.no', generate_password_hash('passord123'), 'admin')
        )
        conn.commit()
        print("Testbruker opprettet: admin / passord123")

    conn.close()


# ─── Hjelpe-dekoratorer ───────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Du må logge inn først.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Ingen tilgang.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated


# ─── Autentisering ────────────────────────────────────────────────

@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f'Velkommen, {user["username"]}!', 'success')
            return redirect(url_for('admin_dashboard' if user['role'] == 'admin' else 'dashboard'))

        flash('Feil brukernavn eller passord.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Du er nå logget ut.', 'info')
    return redirect(url_for('login'))


# ─── Bruker-sider ─────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    # TODO: hent alle saker for innlogget bruker fra databasen
    tickets = []
    return render_template('dashboard.html', tickets=tickets)


@app.route('/ny-sak', methods=['GET', 'POST'])
@login_required
def new_ticket():
    if request.method == 'POST':
        # TODO: hent data fra skjemaet
        # TODO: valider input (tomme felt, lengde osv.)
        # TODO: sett inn ny sak i databasen
        pass

    return render_template('new_ticket.html')


@app.route('/sak/<int:ticket_id>')
@login_required
def view_ticket(ticket_id):
    # TODO: hent saken fra databasen
    # TODO: sjekk at brukeren har lov til å se denne saken
    ticket = None
    return render_template('view_ticket.html', ticket=ticket)


# ─── Admin-sider ──────────────────────────────────────────────────

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    # TODO: hent alle saker fra databasen (JOIN med users-tabellen for å få brukernavn)
    tickets = []
    return render_template('admin_dashboard.html', tickets=tickets)


@app.route('/admin/sak/<int:ticket_id>/oppdater', methods=['POST'])
@login_required
@admin_required
def update_ticket(ticket_id):
    # TODO: hent ny status fra skjemaet
    # TODO: valider at statusen er en av de gyldige verdiene
    # TODO: oppdater saken i databasen
    return redirect(url_for('view_ticket', ticket_id=ticket_id))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)