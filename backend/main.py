from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
import secrets
from banco import criar_banco, conectar
from processamento import extrair_vetor
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # <- IMPORTAR ISSO
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime
import numpy as np

SECRET_KEY = "qR8zW9nX7jH3uL5tB2oF6mV1cY0pK4dS8aE7rN6gU5wJ3iT9lZ2vM8yQ1xC4hA"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Modelos Pydantic (validação de dados) ---
class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str

class Usuario(BaseModel):
    id: int
    nome: str
    email: str

class Pet(BaseModel):
    id: int
    dono_id: int
    nome: str
    especie: Optional[str] = None
    raca: Optional[str] = None
    idade: Optional[int] = None
    foto_url: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    
class PostResponse(BaseModel):
    id: int
    imagem_url: str
    descricao: Optional[str] = None
    timestamp: datetime
    dono_nome: str
    pet_nome: str    

class DonoInfo(BaseModel):
    nome: str
    email: str
    telefone: str # Você pode adicionar o telefone se quiser

class IdentificacaoResponse(BaseModel):
    status: str
    pet_nome: str
    confianca: float
    dono: DonoInfo
# =================================================================
# 3. FUNÇÕES AUXILIARES DE SEGURANÇA
# =================================================================

def verificar_senha(senha_plana, senha_hash):
    return pwd_context.verify(senha_plana, senha_hash)

def get_senha_hash(senha):
    return pwd_context.hash(senha)

def criar_access_token(data: dict):
    to_encode = data.copy()
    # Adicionar expiração aqui se desejar
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    conn = conectar()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user is None:
        raise credentials_exception
    return Usuario(**user)

# =================================================================
# 4. INICIALIZAÇÃO DO APP E ENDPOINTS
# =================================================================

app = FastAPI()
app.mount("/static", StaticFiles(directory="imagens_pets"), name="static")

# --- CORS ---
# Permite que o frontend (rodando em outra porta/endereço) acesse a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, troque por ["http://seu-dominio.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Evento de Startup ---
@app.on_event("startup")
def on_startup():
    criar_banco()
    os.makedirs("imagens_pets", exist_ok=True)
    os.makedirs("imagens_posts", exist_ok=True)


# --- Endpoint Raiz ---
@app.get("/")
def raiz():
    return {"mensagem": "Funcionando!"}

# --- Endpoints de Autenticação ---
@app.post("/usuarios", response_model=Usuario, status_code=status.HTTP_201_CREATED)
def criar_usuario(usuario: UsuarioCreate):
    conn = conectar()
    cursor = conn.cursor()
    senha_hash = get_senha_hash(usuario.senha)
    try:
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)",
            (usuario.nome, usuario.email, senha_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    finally:
        conn.close()
    return {"id": user_id, "nome": usuario.nome, "email": usuario.email}

@app.post("/token", response_model=Token)
async def login_para_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = conectar()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (form_data.username,))
    user = cursor.fetchone()
    conn.close()

    if not user or not verificar_senha(form_data.password, user["senha_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = criar_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}


# --- Endpoints de Pets (Protegidos) ---

@app.post("/pets", response_model=Pet, status_code=status.HTTP_201_CREATED)
async def cadastrar_pet(
    nome: str = Form(...),
    especie: str = Form(...),
    raca: str = Form(...),
    idade: int = Form(...),
    file: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user)
):
    # Salva a imagem
    file_extension = file.filename.split(".")[-1]
    file_name = f"{secrets.token_hex(8)}.{file_extension}"
    caminho_imagem = f"imagens_pets/{file_name}"

    with open(caminho_imagem, "wb") as f:
        f.write(await file.read())

    # Extrai o vetor da imagem
    vetor_iris = extrair_vetor(caminho_imagem)
    if not vetor_iris:
        raise HTTPException(status_code=500, detail="Não foi possível processar a imagem do pet.")

    # Salva o pet no banco de dados
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO pets (dono_id, nome, especie, raca, idade, vetor_iris, foto_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (current_user.id, nome, especie, raca, idade, vetor_iris, file_name)
    )
    conn.commit()
    pet_id = cursor.lastrowid
    conn.close()

    return {
        "id": pet_id, "dono_id": current_user.id, "nome": nome, "especie": especie,
        "raca": raca, "idade": idade, "foto_url": caminho_imagem,
        "foto_url": file_name
    }

@app.get("/pets", response_model=List[Pet])
async def listar_meus_pets(current_user: Usuario = Depends(get_current_user)):
    conn = conectar()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pets WHERE dono_id = ?", (current_user.id,))
    pets_rows = cursor.fetchall()
    conn.close()

    # AQUI ESTÁ A CORREÇÃO:
    # Converte a lista de 'sqlite3.Row' em uma lista de dicionários.
    pets = [dict(row) for row in pets_rows]
    return pets

@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def criar_post(
    pet_id: int = Form(...),
    descricao: str = Form(...),
    file: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user)
):
    # Salva a imagem na pasta de posts
    file_extension = file.filename.split(".")[-1]
    file_name = f"{secrets.token_hex(10)}.{file_extension}"
    caminho_imagem = f"imagens_posts/{file_name}"

    with open(caminho_imagem, "wb") as f:
        f.write(await file.read())
    
    # Insere o post no banco de dados
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO posts (usuario_id, pet_id, imagem_url, descricao) VALUES (?, ?, ?, ?)",
        (current_user.id, pet_id, file_name, descricao)
    )
    conn.commit()
    conn.close()

    return {"status": "ok", "detail": "Post criado com sucesso"}

@app.get("/feed", response_model=List[PostResponse])
async def get_feed(current_user: Usuario = Depends(get_current_user)):
    conn = conectar()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query que busca os posts e junta com dados do usuário e do pet
    cursor.execute("""
        SELECT 
            p.id, p.imagem_url, p.descricao, p.timestamp,
            u.nome as dono_nome,
            pet.nome as pet_nome
        FROM posts p
        JOIN usuarios u ON p.usuario_id = u.id
        JOIN pets pet ON p.pet_id = pet.id
        ORDER BY p.timestamp DESC
    """)
    posts_rows = cursor.fetchall()
    conn.close()

    # Converte as linhas do DB em dicionários
    feed = [dict(row) for row in posts_rows]
    return feed

@app.post("/identificar_pet")
async def identificar_pet(file: UploadFile = File(...)):
    # 1. Salva a imagem temporariamente
    temp_file_name = f"temp_{secrets.token_hex(8)}_{file.filename}"
    caminho_imagem_temp = f"imagens_posts/{temp_file_name}"

    with open(caminho_imagem_temp, "wb") as f:
        f.write(await file.read())
    
    # 2. Extrai o vetor da imagem enviada
    try:
        vetor_encontrado_str = extrair_vetor(caminho_imagem_temp)
        if not vetor_encontrado_str:
            raise HTTPException(status_code=400, detail="Imagem inválida ou não processável.")
        vetor_encontrado = np.array([float(v) for v in vetor_encontrado_str.split(',')])
    finally:
        # Garante que a imagem temporária seja deletada
        os.remove(caminho_imagem_temp)

    # 3. Busca todos os pets e seus vetores no banco
    conn = conectar()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, vetor_iris, dono_id FROM pets")
    todos_pets = cursor.fetchall()
    
    if not todos_pets:
        conn.close()
        return {"status": "erro", "mensagem": "Nenhum pet cadastrado no sistema."}

    melhor_pet_encontrado = None
    maior_similaridade = 0.0

    # 4. Compara o vetor da imagem com todos os vetores do banco
    for pet in todos_pets:
        vetor_db = np.array([float(v) for v in pet["vetor_iris"].split(',')])
        
        # Cálculo da Similaridade de Cosseno com NumPy
        dot_product = np.dot(vetor_encontrado, vetor_db)
        norm_encontrado = np.linalg.norm(vetor_encontrado)
        norm_db = np.linalg.norm(vetor_db)
        similaridade = dot_product / (norm_encontrado * norm_db)

        if similaridade > maior_similaridade:
            maior_similaridade = similaridade
            melhor_pet_encontrado = pet

    # 5. Verifica se a similaridade ultrapassa um limite de confiança
    LIMITE_CONFIANCA = 0.85 # Valor entre 0 e 1. Ajuste conforme os testes.

    if maior_similaridade > LIMITE_CONFIANCA:
        # Busca os dados do dono
        cursor.execute("SELECT nome, email FROM usuarios WHERE id = ?", (melhor_pet_encontrado["dono_id"],))
        dono = cursor.fetchone()
        conn.close()

        return {
            "status": "ok",
            "pet_nome": melhor_pet_encontrado["nome"],
            "confianca": maior_similaridade,
            "dono": {
                "nome": dono["nome"],
                "email": dono["email"]
            }
        }
    else:
        # Se a maior similaridade for baixa, consideramos que não encontrou
        conn.close()
        return {"status": "erro", "mensagem": "Nenhum pet compatível encontrado."}