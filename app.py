from flask import Flask, jsonify
from cryptography.fernet import Fernet
import sqlite3, os

app = Flask(__name__)

# IP simulada fija de mi salud 
IP_FIJA = "192.168.1.100" 

# Generar o usar clave de cifrado
FERNET_KEY = os.environ.get("FERNET_KEY")
if not FERNET_KEY:
    FERNET_KEY = Fernet.generate_key().decode()
    print("🔑 FERNET_KEY generada (guárdala):", FERNET_KEY)
f = Fernet(FERNET_KEY.encode())

# Base de datos local (solo guarda IP cifrada)
DB = "database.db"

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE IF NOT EXISTS ip_clinica (id INTEGER PRIMARY KEY, ip_enc TEXT, ts DATETIME DEFAULT (datetime('now')))")
    conn.commit()
    conn.close()

@app.before_first_request
def setup():
    init_db()

# Ruta para encriptar la IP simulada
@app.route("/encrypt-ip", methods=["GET"])
def encrypt_ip():
    ip_enc = f.encrypt(IP_FIJA.encode()).decode()
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO ip_clinica (ip_enc) VALUES (?)", (ip_enc,))
    conn.commit()
    conn.close()
    return jsonify({
        "status": "ok",
        "ip_original": IP_FIJA,
        "ip_encriptada": ip_enc
    })

# Ruta para consultar los registros guardados
@app.route("/all", methods=["GET"])
def all_ips():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id, ip_enc, ts FROM ip_clinica ORDER BY id DESC")
    data = cur.fetchall()
    conn.close()
    return jsonify(data)

# Ejecutar app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
