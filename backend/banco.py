import sqlite3

DATABASE_URL = "petid.db"

def criar_banco():
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dono_id INTEGER NOT NULL,
        nome TEXT NOT NULL,
        especie TEXT,
        raca TEXT,
        idade INTEGER,
        vetor_iris TEXT,
        foto_url TEXT,
        FOREIGN KEY (dono_id) REFERENCES usuarios (id)
        
        
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        pet_id INTEGER NOT NULL,
        imagem_url TEXT NOT NULL,
        descricao TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
        FOREIGN KEY (pet_id) REFERENCES pets (id)
    )
    """)
    
    conn.commit()
    conn.close()
    print("Banco de dados criado com sucesso.")
    
    
def conectar():
    return sqlite3.connect(DATABASE_URL)
    
    