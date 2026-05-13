import pyodbc
import uuid
import datetime
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configurazione Connessione
DB_CONN = (
    "DRIVER={MySQL ODBC 9.7 Unicode Driver};"
    "SERVER=127.0.0.1;PORT=3305;"
    "DATABASE=SimulazioneEsame;UID=root;PWD=SimulazioneEsame;"
)

def get_conn():
    return pyodbc.connect(DB_CONN, autocommit=True)

# Helpers
def valida_token(token):
    if not token: return False
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT DataOraScadenzaToken FROM TUsers WHERE Token = ?", (token,))
    row = cur.fetchone()
    conn.close()
    return row and row[0] and row[0] > datetime.datetime.now()

def calcola_codice_fiscale(cognome, nome, nascita, sesso, cc):
    mesi = "ABCDEHLMPRST"
    get_c = lambda s: ([c for c in s.upper() if c not in 'AEIOU '] + [c for c in s.upper() if c in 'AEIOU'] + ['X']*3)[:3]
    codice = f"{''.join(get_c(cognome))}{''.join(get_c(nome))}{nascita.year%100:02d}{mesi[nascita.month-1]}{nascita.day + (40 if sesso=='F' else 0):02d}{cc}"
    
    dispari = {'A':1,'B':0,'C':5,'D':7,'E':9,'F':13,'G':15,'H':17,'I':19,'J':21,'K':2,'L':4,'M':18,'N':20,'O':11,'P':3,'Q':6,'R':8,'S':12,'T':14,'U':16,'V':10,'W':22,'X':25,'Y':24,'Z':23}
    dispari.update({str(i): [1,0,5,7,9,13,15,17,19,21][i] for i in range(10)})
    pari = {chr(i+65): i for i in range(26)}
    pari.update({str(i): i for i in range(10)})
    
    somma = sum(dispari[c] for c in codice[::2]) + sum(pari[c] for c in codice[1::2])
    return codice + chr(somma % 26 + 65)

# CORS Middleware (per chiamate da Web/MAUI)
@app.after_request
def add_cors(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST')
    return response

# 2.1 Registrazione
@app.route('/api/registrazione', methods=['POST'])
def registrazione():
    data = request.json
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT 1 FROM TUsers WHERE Email = ?", (data['Email'],))
    if cur.fetchone():
        return jsonify({"success": False, "message": "Utente già registrato"}), 400
    
    pwd_hash = generate_password_hash(data['Password'])
    cur.execute("INSERT INTO TUsers (Email, Password) VALUES (?, ?)", (data['Email'], pwd_hash))
    conn.close()
    return jsonify({"success": True, "message": "Utente registrato correttamente"})

# 2.2 Login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT UserID, Password FROM TUsers WHERE Email = ?", (data['Email'],))
    user = cur.fetchone()
    
    if user and check_password_hash(user[1], data['Password']):
        token = uuid.uuid4().hex
        expiry = datetime.datetime.now() + datetime.timedelta(minutes=30)
        cur.execute("UPDATE TUsers SET Token = ?, DataOraScadenzaToken = ? WHERE UserID = ?", 
                    (token, expiry, user[0]))
        conn.close()
        return jsonify({"success": True, "token": token, "message": "Login effettuato correttamente"})
    conn.close()
    return jsonify({"success": False, "message": "Credenziali errate"}), 401

# 2.3 Logout
@app.route('/api/logout', methods=['POST'])
def logout():
    data = request.json
    if not valida_token(data['Token']):
        return jsonify({"success": False, "message": "Token non valido o scaduto"}), 401
    conn = get_conn(); cur = conn.cursor()
    cur.execute("UPDATE TUsers SET Token = NULL, DataOraScadenzaToken = NULL WHERE Token = ?", (data['Token'],))
    conn.close()
    return jsonify({"success": True, "message": "Logout effettuato correttamente"})

# 2.4 Modifica Password
@app.route('/api/modifica-password', methods=['POST'])
def modifica_password():
    data = request.json
    if not valida_token(data['Token']):
        return jsonify({"success": False, "message": "Token non valido"}), 401
        
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT Password FROM TUsers WHERE Email = ? AND Token = ?", (data['Email'], data['Token']))
    row = cur.fetchone()
    if row and check_password_hash(row[0], data['VecchiaPassword']):
        cur.execute("UPDATE TUsers SET Password = ? WHERE Email = ?", 
                    (generate_password_hash(data['NuovaPassword']), data['Email']))
        conn.close()
        return jsonify({"success": True, "message": "Password modificata correttamente"})
    conn.close()
    return jsonify({"success": False, "message": "Credenziali errate"}), 401

# 2.5 Lista Dipendenti
@app.route('/api/lista-dipendenti', methods=['POST'])
def lista_dipendenti():
    data = request.json
    if not valida_token(data['Token']):
        return jsonify({"success": False, "message": "Token non valido"}), 401
        
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT DipendenteID, Cognome, Nome, DataNascita, Sesso, ComuneNascita, ProvinciaNascita FROM TDipendenti")
    rows = cur.fetchall()
    conn.close()
    
    dipendenti = [dict(zip([c[0] for c in cur.description], r)) for r in rows]
    return jsonify({"success": True, "dipendenti": dipendenti})

# 2.6 Codice Fiscale
@app.route('/api/codice-fiscale', methods=['POST'])
def codice_fiscale():
    data = request.json
    if not valida_token(data['Token']):
        return jsonify({"success": False, "message": "Token non valido"}), 401
        
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT Cognome, Nome, DataNascita, Sesso, ComuneNascita, ProvinciaNascita FROM TDipendenti WHERE DipendenteID = ?", (data['DipendenteID'],))
    emp = cur.fetchone()
    if not emp: return jsonify({"success": False, "message": "Dipendente non trovato"}), 404

    # Lookup Codice Catastale
    cur.execute("SELECT CodiceCatastale FROM TCodiciCatastali WHERE Comune = ? AND Provincia = ?", (emp[4], emp[5]))
    cc_row = cur.fetchone()
    if not cc_row: return jsonify({"success": False, "message": "Codice catastale non trovato"}), 404
    
    conn.close()
    cf = calcola_codice_fiscale(emp[0], emp[1], emp[2], emp[3], cc_row[0])
    return jsonify({"success": True, "CodiceFiscale": cf})

if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")