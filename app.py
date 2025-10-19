from flask import Flask, request, jsonify
from flask_cors import CORS 
from cryptography.fernet import Fernet
import sqlite3, os

# Inicializar la app
app = Flask(__name__)
CORS(app)  # 👈 Habilita CORS para todas las rutas

# Generar o recuperar la clave de cifrado
FERNET_KEY = os.environ.get("FERNET_KEY")
if not FERNET_KEY:
    FERNET_KEY = Fernet.generate_key().decode()
    print("🔑 FERNET_KEY generada (guárdala):", FERNET_KEY)
f = Fernet(FERNET_KEY.encode())

DB = "database.db"

# Crear la base de datos si no existe
def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS accesos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_enc TEXT,
            ts DATETIME DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()

# Inicializar la base de datos al inicio
with app.app_context():
    init_db()

# 🔹 Ruta principal
@app.route("/")
def home():
    return "<h2>✅ Backend de Mi Salud activo</h2><p>Usa /log-ip o /all para probar las funciones.</p>"

# Obtener la IP real del cliente
def get_ip(req):
    xff = req.headers.get("X-Forwarded-For", "")
    if xff:
        return xff.split(",")[0].strip()
    return req.remote_addr

# 🔹 Registrar una IP encriptada (POST)
@app.route("/log-ip", methods=["POST"])
def log_ip():
    ip = get_ip(request)
    ip_enc = f.encrypt(ip.encode()).decode()

    print("🧠 IP recibida:", ip)
    print("🔒 IP encriptada:", ip_enc)

    try:
        conn = sqlite3.connect(DB)
        conn.execute("INSERT INTO accesos (ip_enc) VALUES (?)", (ip_enc,))
        conn.commit()
        conn.close()
        print("✅ IP guardada en la base de datos.")
    except Exception as e:
        print("⚠️ Error guardando IP:", e)

    return jsonify({"status": "ok", "ip_encrypted": ip_enc})


# 🔹 Ver todas las IPs guardadas
@app.route("/all", methods=["GET"])
def all_ips():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id, ip_enc, ts FROM accesos ORDER BY id DESC")
    data = cur.fetchall()
    conn.close()
    return jsonify(data)

# 🔹 Encriptar IP fija simulada (opcional)
@app.route("/encriptar-ip-fija")
def encriptar_ip_fija():
    ip_fija = "181.51.233.120"  # IP simulada de la clínica
    ip_enc = f.encrypt(ip_fija.encode()).decode()
    return jsonify({"ip_fija": ip_fija, "ip_encriptada": ip_enc})

# Iniciar el servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

