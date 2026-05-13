import pyodbc
import pandas as pd
import sqlalchemy
import urllib

# Configura i parametri di connessione (modifica in base al tuo DB)
# Esempio per SQL Server:
conn_str = (
    "DRIVER={MySQL ODBC 9.7 Unicode Driver};"
    "SERVER=127.0.0.1;PORT=3305;"
    "DATABASE=SimulazioneEsame;UID=root;PWD=SimulazioneEsame;"
)

try:
    # 1. Connessione
    conn = pyodbc.connect(conn_str, autocommit=True)
    cursor = conn.cursor()

    # 2. Creazione Database (Nota: CREATE DATABASE non può girare in una transazione)
    cursor.execute("IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'SimulazioneEsame') BEGIN CREATE DATABASE SimulazioneEsame END")
    cursor.execute("USE SimulazioneEsame")

    # 3. Creazione Tabella TUsers
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TUsers' AND xtype='U')
        CREATE TABLE TUsers (
            UserID INT IDENTITY(1,1) PRIMARY KEY,
            Email VARCHAR(100) UNIQUE NOT NULL,
            Password VARCHAR(255) NOT NULL,
            Token VARCHAR(255) DEFAULT NULL,
            DataOraScadenzaToken DATETIME DEFAULT NULL
        )
    """)

    # 4. Creazione Tabella TDipendenti
    # Nota: SQL Server non ha ENUM, usiamo un vincolo CHECK
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TDipendenti' AND xtype='U')
        CREATE TABLE TDipendenti (
            DipendenteID INT IDENTITY(1,1) PRIMARY KEY,
            Cognome VARCHAR(50) NOT NULL,
            Nome VARCHAR(50) NOT NULL,
            DataNascita DATE NOT NULL,
            Sesso CHAR(1) CHECK (Sesso IN ('M', 'F')) NOT NULL,
            ComuneNascita VARCHAR(100) NOT NULL,
            ProvinciaNascita VARCHAR(2) NOT NULL
        )
    """)

    # 5. Inserimento Dati (Uso dei segnaposto '?' per pyodbc)
    cursor.execute("SELECT COUNT(*) FROM TDipendenti")
    if cursor.fetchone()[0] == 0:
        sql_insert = """
            INSERT INTO TDipendenti (Cognome, Nome, DataNascita, Sesso, ComuneNascita, ProvinciaNascita) 
            VALUES (?, ?, ?, ?, ?, ?)
        """
        valori = [
            ('Rossi', 'Mario', '1985-03-12', 'M', 'Roma', 'RM'),
            ('Verdi', 'Anna', '1990-07-22', 'F', 'Milano', 'MI'),
            ('Bianchi', 'Luca', '1978-11-05', 'M', 'Napoli', 'NA')
        ]
        cursor.executemany(sql_insert, valori)

    # 6. Tabella Codici Catastali
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TCodiciCatastali' AND xtype='U')
        CREATE TABLE TCodiciCatastali (
            ID INT IDENTITY(1,1) PRIMARY KEY,
            Comune VARCHAR(100) NOT NULL,
            Provincia VARCHAR(2) NOT NULL,
            CodiceCatastale VARCHAR(4) NOT NULL
        )
    """)
    cursor.execute("CREATE INDEX idx_comune_prov ON TCodiciCatastali (Comune, Provincia)")

    # 2. "Passiamo" pyodbc a SQLAlchemy
    # urllib serve a codificare la stringa per renderla leggibile all'engine
    params = urllib.parse.quote_plus(conn_str)
    engine = sqlalchemy.create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

    # 3. Pandas usa l'engine (e quindi pyodbc) per caricare i dati
    df = pd.read_csv('C:/percorso/codici.csv', quotechar='"')
    df.to_sql('TCodiciCatastali', con=engine, if_exists='append', index=False)

except Exception as e:
    print(f"Errore durante l'esecuzione: {e}")

finally:
    if 'conn' in locals():
        conn.close()