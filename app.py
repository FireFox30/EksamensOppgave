from flask import Flask, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
from functools import wraps

app = Flask(__name__)
app.secret_key = 'superhemmelig' 

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_PORT'] = 3307
app.config['MYSQL_USER'] = 'ticket_admin'
app.config['MYSQL_PASSWORD'] = 'abc123'
app.config['MYSQL_DB'] = 'helpdesk_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


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

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

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
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'annet')

        if not title or not description:
            flash('Tittel og beskrivelse er påkrevd.', 'danger')
        else:
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO tickets (user_id, title, description, category) VALUES (%s, %s, %s, %s)",
                (session['user_id'], title, description, category)
            )
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('dashboard'))

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
    app.run(debug=True)