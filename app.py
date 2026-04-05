from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__, static_folder='static')
CORS(app)

DB = 'reservas.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS reservas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                huesped TEXT NOT NULL,
                checkin TEXT NOT NULL,
                checkout TEXT NOT NULL,
                notas TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/reservas', methods=['GET'])
def listar():
    with get_db() as conn:
        rows = conn.execute('SELECT * FROM reservas ORDER BY checkin').fetchall()
        return jsonify([dict(r) for r in rows])

@app.route('/reservas', methods=['POST'])
def crear():
    data = request.json
    if not data or not data.get('huesped') or not data.get('checkin') or not data.get('checkout'):
        return jsonify({'error': 'Faltan campos obligatorios'}), 400
    if data['checkin'] >= data['checkout']:
        return jsonify({'error': 'La salida debe ser posterior a la entrada'}), 400
    with get_db() as conn:
        cur = conn.execute(
            'INSERT INTO reservas (huesped, checkin, checkout, notas) VALUES (?, ?, ?, ?)',
            (data['huesped'], data['checkin'], data['checkout'], data.get('notas', ''))
        )
        return jsonify({'id': cur.lastrowid, **data}), 201

@app.route('/reservas/<int:id>', methods=['DELETE'])
def eliminar(id):
    with get_db() as conn:
        conn.execute('DELETE FROM reservas WHERE id = ?', (id,))
        return jsonify({'ok': True})

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
