from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
import os, secrets
from banco import criar_banco, conectar
from processamento import extrair_vetor_cnn
import qrcode

app = FastAPI()
@app.get("/")
def raiz():
    return {"mensagem": "API do Pet Iris rodando! 🐶🐱👁️"}

criar_banco()
os.makedirs("imagens", exist_ok=True)

# Cadastro de pet
@app.post("/cadastrar_pet")
async def cadastrar_pet(
    nome_pet: str = Form(...),
    especie: str = Form(...),
    raca: str = Form(...),
    idade: int = Form(...),
    nome_dono: str = Form(...),
    telefone: str = Form(...),
    email: str = Form(...),
    file: UploadFile = File(...)
):
    caminho_imagem = f"imagens/{file.filename}"
    with open(caminho_imagem, "wb") as f:
        f.write(await file.read())

    vetor = extrair_vetor_cnn(caminho_imagem)
    chave_acesso = secrets.token_hex(8)

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pets (nome, especie, raca, idade, vetor_iris, dono_nome, telefone, email, chave_acesso)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (nome_pet, especie, raca, idade, vetor, nome_dono, telefone, email, chave_acesso))
    pet_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Gera QR Code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"PET_ID:{pet_id}|CHAVE:{chave_acesso}")
    qr.make(fit=True)
    img_qr = qr.make_image(fill='black', back_color='white')
    qr_path = f"imagens/qr_{pet_id}.png"
    img_qr.save(qr_path)

    return {"status":"ok", "pet_id":pet_id, "chave_acesso":chave_acesso}

# Pega QR Code
@app.get("/qr/{pet_id}")
def pegar_qr(pet_id: int):
    qr_path = f"imagens/qr_{pet_id}.png"
    if os.path.exists(qr_path):
        return FileResponse(qr_path, media_type="image/png")
    return {"status":"erro","mensagem":"QR Code não encontrado"}

# Identificação do pet perdido
@app.post("/identificar_pet")
async def identificar_pet(file: UploadFile = File(...), chave: str = Form(...)):
    caminho_imagem = f"imagens/temp_{file.filename}"
    with open(caminho_imagem, "wb") as f:
        f.write(await file.read())

    vetor_input = extrair_vetor_cnn(caminho_imagem)
    vetor_input = list(map(float, vetor_input.split(',')))

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pets")
    pets = cursor.fetchall()
    conn.close()

    melhor_sim = 0
    pet_encontrado = None

    for pet in pets:
        vetor_pet = list(map(float, pet[5].split(',')))
        # Similaridade cosseno
        dot = sum([vetor_pet[i]*vetor_input[i] for i in range(len(vetor_pet))])
        norm_pet = sum([v**2 for v in vetor_pet])**0.5
        norm_input = sum([v**2 for v in vetor_input])**0.5
        sim = dot/(norm_pet*norm_input)
        if sim > melhor_sim:
            melhor_sim = sim
            pet_encontrado = pet

    if pet_encontrado and melhor_sim > 0.8:
        if chave != pet_encontrado[9]:  # coluna chave_acesso
            return {"status":"erro","mensagem":"Chave de acesso inválida"}
        return {
            "status":"ok",
            "nome_pet":pet_encontrado[1],
            "dono":{"nome":pet_encontrado[6],"telefone":pet_encontrado[7],"email":pet_encontrado[8]},
            "confianca":melhor_sim
        }

    return {"status":"erro","mensagem":"Pet não encontrado"}
