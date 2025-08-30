// VERSÃO DEFINITIVA - TESTE FINAL - 30/08/2025

document.addEventListener("DOMContentLoaded", () => {
    const API_URL = "http://127.0.0.1:8000";

    // Elementos da UI
    const loginView = document.getElementById("login-view");
    const registerView = document.getElementById("register-view");
    const dashboardView = document.getElementById("dashboard-view");
    const identificationView = document.getElementById("identification-view");

    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
    const addPetForm = document.getElementById("add-pet-form");
    const addPostForm = document.getElementById("add-post-form");
    const identificationForm = document.getElementById("identification-form");

    const showRegisterLink = document.getElementById("show-register");
    const showLoginLink = document.getElementById("show-login");
    const showIdentificationLink = document.getElementById("show-identification");
    const backToLoginLink = document.getElementById("back-to-login");
    const logoutButton = document.getElementById("logout-button");

    const loginError = document.getElementById("login-error");
    const registerError = document.getElementById("register-error");
    const petSuccessMsg = document.getElementById("pet-success");
    const postSuccessMsg = document.getElementById("post-success");
    const identificationResult = document.getElementById("identification-result");

    const myPetsList = document.getElementById("my-pets-list");
    const petSelect = document.getElementById("pet-select");
    const feedPosts = document.getElementById("feed-posts");

    const identificationButton = document.getElementById("identification-button");

    // =================================================================
    // CONTROLE DE NAVEGAÇÃO ENTRE TELAS
    // =================================================================

    function showView(viewId) {
        document.querySelectorAll(".view").forEach(view => view.classList.remove("active"));
        document.getElementById(viewId).classList.add("active");
    }

    showRegisterLink.addEventListener("click", (e) => {
        e.preventDefault();
        showView("register-view");
    });

    showLoginLink.addEventListener("click", (e) => {
        e.preventDefault();
        showView("login-view");
    });

    showIdentificationLink.addEventListener("click", (e) => {
        e.preventDefault();
        showView("identification-view");
    });

    backToLoginLink.addEventListener("click", (e) => {
        e.preventDefault();
        showView("login-view");
    });

    logoutButton.addEventListener("click", () => {
        localStorage.removeItem("petIdToken");
        showView("login-view");
        myPetsList.innerHTML = "";
    });

    // =================================================================
    // LÓGICA DE AUTENTICAÇÃO
    // =================================================================

    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        registerError.textContent = "";
        const formData = new FormData(registerForm);
        const data = Object.fromEntries(formData.entries());
        try {
            const response = await fetch(`${API_URL}/usuarios`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            if (response.status === 201) {
                alert("Cadastro realizado com sucesso! Faça o login.");
                registerForm.reset();
                showView("login-view");
            } else {
                const errorData = await response.json();
                registerError.textContent = errorData.detail || "Erro ao cadastrar.";
            }
        } catch (error) {
            registerError.textContent = "Não foi possível conectar ao servidor.";
        }
    });

    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        loginError.textContent = "";
        const formData = new FormData(loginForm);
        const params = new URLSearchParams(formData);
        try {
            const response = await fetch(`${API_URL}/token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: params,
            });
            if (response.ok) {
                const data = await response.json();
                localStorage.setItem("petIdToken", data.access_token);
                await navigateToDashboard();
            } else {
                loginError.textContent = "Email ou senha incorretos.";
            }
        } catch (error) {
            loginError.textContent = "Não foi possível conectar ao servidor.";
        }
    });

    // =================================================================
    // LÓGICA DO DASHBOARD (LOGADO)
    // =================================================================

    async function navigateToDashboard() {
        const token = localStorage.getItem("petIdToken");
        if (!token) return;
        showView("dashboard-view");
        await fetchMyPets();
        await fetchFeed();
    }

    addPetForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        petSuccessMsg.textContent = "";
        const token = localStorage.getItem("petIdToken");
        const formData = new FormData(addPetForm);
        try {
            const response = await fetch(`${API_URL}/pets`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData,
            });
            if (response.status === 201) {
                petSuccessMsg.textContent = "Pet cadastrado com sucesso!";
                addPetForm.reset();
                await fetchMyPets();
            } else {
                const errorData = await response.json();
                alert(`Erro ao cadastrar pet: ${errorData.detail}`);
            }
        } catch (error) {
            alert("Erro de conexão ao cadastrar pet.");
        }
    });

    addPostForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        postSuccessMsg.textContent = "";
        const token = localStorage.getItem("petIdToken");
        const formData = new FormData(addPostForm);
        try {
            const response = await fetch(`${API_URL}/posts`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData,
            });
            if (response.ok) {
                postSuccessMsg.textContent = "Post publicado com sucesso!";
                addPostForm.reset();
                await fetchFeed();
            } else {
                alert("Erro ao publicar o post.");
            }
        } catch (error) {
            alert("Erro de conexão ao publicar o post.");
        }
    });

    async function fetchMyPets() {
        const token = localStorage.getItem("petIdToken");
        if (!token) return;
        try {
            const response = await fetch(`${API_URL}/pets`, {
                method: 'GET',
                headers: { 'Authorization': `Bearer ${token}` },
            });
            if (response.ok) {
                const pets = await response.json();
                myPetsList.innerHTML = "";
                petSelect.innerHTML = "";
                if (pets.length === 0) {
                    myPetsList.innerHTML = "<p>Você ainda não tem pets cadastrados.</p>";
                } else {
                    pets.forEach(pet => {
                        const petElement = document.createElement("div");
                        petElement.className = "pet-item";
                        const imageUrl = `${API_URL}/static/${pet.foto_url}`;
                        petElement.innerHTML = `
                            <img src="${imageUrl}" alt="Foto de ${pet.nome}">
                            <div>
                                <h3>${pet.nome}</h3>
                                <p>${pet.especie} - ${pet.raca}</p>
                            </div>
                        `;
                        myPetsList.appendChild(petElement);

                        const option = document.createElement("option");
                        option.value = pet.id;
                        option.textContent = pet.nome;
                        petSelect.appendChild(option);
                    });
                }
            }
        } catch (error) {
            myPetsList.innerHTML = "<p>Erro ao carregar seus pets.</p>";
        }
    }

    async function fetchFeed() {
        const token = localStorage.getItem("petIdToken");
        if (!token) return;
        try {
            const response = await fetch(`${API_URL}/feed`, {
                headers: { 'Authorization': `Bearer ${token}` },
            });
            if (response.ok) {
                const posts = await response.json();
                feedPosts.innerHTML = "";
                posts.forEach(post => {
                    const postElement = document.createElement("div");
                    postElement.className = "post-card";
                    // CORREÇÃO: Removido 'imagens_posts/' do caminho da imagem
                    const imageUrl = `${API_URL}/static/${post.imagem_url}`; 

                    postElement.innerHTML = `
                        <div class="post-header">
                            <span class="user-name">${post.dono_nome}</span> com 
                            <span class="pet-name">${post.pet_nome}</span>
                        </div>
                        <img src="${imageUrl}" alt="Post sobre ${post.pet_nome}" class="post-image">
                        <div class="post-caption">
                            <p>${post.descricao}</p>
                        </div>
                    `;
                    feedPosts.appendChild(postElement);
                });
            }
        } catch (error) {
            feedPosts.innerHTML = "<p>Erro ao carregar o feed.</p>";
        }
    }

    // =================================================================
    // LÓGICA DE IDENTIFICAÇÃO (PÚBLICO)
    // =================================================================
    identificationButton.addEventListener("click", async () => {
        // Não precisamos mais do 'e.preventDefault()' aqui
        
        identificationResult.innerHTML = "<p>Processando imagem, por favor aguarde...</p>";
        
        // Precisamos pegar o formulário para extrair os dados
        const formData = new FormData(identificationForm);

        // Verificamos se um arquivo foi selecionado
        const fileInput = identificationForm.querySelector('input[type="file"]');
        if (!fileInput.files || fileInput.files.length === 0) {
            identificationResult.innerHTML = "<p class='error-message'>Por favor, selecione uma imagem.</p>";
            return;
        }

        try {
            const response = await fetch(`${API_URL}/identificar_pet`, {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();
            
            if (data.status === "ok") {
                const confiancaPercentual = (data.confianca * 100).toFixed(2);
                identificationResult.innerHTML = `
                    <div class="success-message">
                        <h3>Pet Encontrado!</h3>
                        <p><strong>Nome do Pet:</strong> ${data.pet_nome}</p>
                        <p><strong>Nome do Dono:</strong> ${data.dono.nome}</p>
                        <p><strong>Email do Dono:</strong> ${data.dono.email}</p>
                        <p><strong>Confiança da Identificação:</strong> ${confiancaPercentual}%</p>
                    </div>
                `;
            } else {
                identificationResult.innerHTML = `
                    <p class="error-message">${data.mensagem || 'Pet não encontrado.'}</p>
                `;
            }
        } catch (error) {
            identificationResult.innerHTML = "<p class='error-message'>Erro de conexão ao tentar identificar.</p>";
        }
        
        identificationForm.reset();
    });

    // =================================================================
    // INICIALIZAÇÃO DO APP
    // =================================================================
    function init() {
        const token = localStorage.getItem("petIdToken");
        if (token) {
            navigateToDashboard();
        } else {
            showView("login-view");
        }
    }

    init();
});