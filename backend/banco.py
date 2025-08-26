import sqlite3

def criar_banco():
    conn = sqlite3.connect("pets.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        especie TEXT,
        raca TEXT,
        idade INTEGER,
        vetor_iris TEXT,
        dono_nome TEXT,
        telefone TEXT,
        email TEXT,
        chave_acesso TEXT
    )
    """)
    conn.commit()
    conn.close()

def conectar():
    return sqlite3.connect("pets.db")