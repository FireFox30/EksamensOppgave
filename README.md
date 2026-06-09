# IT Helpdesk – Eksamenprosjekt

## Prosjektstruktur

```
helpdesk/
├── app.py                  # Flask-applikasjon (ruter, logikk)
├── helpdesk.db             # SQLite-database (opprettes automatisk)
├── requirements.txt        # Python-avhengigheter
├── README.md
├── static/
│   ├── css/
│       ├── style.css
│   └── js/
│       ├── admin.js
└── templates/
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── new_ticket.html
    ├── view_ticket.html
    └── admin_dashboard.html
```

## Oppsett

### 1. Installer avhengigheter
```bash
pip install flask
```

### 2. Start applikasjonen
```bash
python3 app.py
```

Første gang appen starter opprettes databasen og en admin-bruker automatisk.

Åpne nettleseren på: http://127.0.0.1:5000

## Innlogging (testbruker)

| Brukernavn | Passord     | Rolle |
|------------|-------------|-------|
| admin      | passord123  | admin |
| aksel      | IMKuben1337!| bruker|

## Funksjonalitet

| Funksjon             | Hvem   |
|----------------------|--------|
| Logg inn / ut        | Alle   |
| Se egne saker        | Bruker |
| Melde inn ny sak     | Bruker |
| Se alle saker        | Admin  |
| Oppdatere status     | Admin  |

## Sikkerhetspunkter

- Input valideres server-side
- Brukere kan kun se egne saker
- Rollebasert tilgangskontroll (bruker / admin)
- Session-basert autentisering