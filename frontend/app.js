const API_URL = "http://127.0.0.1:8000";

const formCadastro = document.getElementById('formCadastro');
const resCadastro = document.getElementById('resCadastro');
const qrCadastro = document.getElementById('qrCadastro');

const formIdentificacao = document.getElementById('formIdentificacao');
const resIdentificacao = document.getElementById('resIdentificacao');

// Cadastro do pet
formCadastro.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(formCadastro);

    const response = await fetch(`${API_URL}/cadastrar_pet`, {
        method: 'POST',
        body: formData
    });

    const data = await response.json();
    if(data.status === "ok") {
        resCadastro.textContent = `Pet cadastrado com sucesso! ID: ${data.pet_id}`;
        formCadastro.reset();

        qrCadastro.src = `${API_URL}/qr/${data.pet_id}`;
        qrCadastro.style.display = "block";
    } else {
        resCadastro.textContent = `Erro: ${data.mensagem}`;
    }
});

// Identificação do pet perdido
formIdentificacao.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(formIdentificacao);
    formData.append('chave', formIdentificacao.chave.value);

    const response = await fetch(`${API_URL}/identificar_pet`, {
        method: 'POST',
        body: formData
    });

    const data = await response.json();
    if(data.status === "ok") {
        resIdentificacao.innerHTML = `
            🐶 Pet encontrado: ${data.nome_pet} <br>
            👤 Dono: ${data.dono.nome} <br>
            📞 Telefone: ${data.dono.telefone} <br>
            ✉️ Email: ${data.dono.email} <br>
            🔎 Confiança: ${(data.confianca*100).toFixed(2)}%
        `;
        formIdentificacao.reset();
    } else {
        resIdentificacao.textContent = "Pet não encontrado ou chave inválida!";
    }
});
