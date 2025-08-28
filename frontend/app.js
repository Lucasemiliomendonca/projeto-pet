document.addEventListener("DOMContentLoaded", () => {
    const API_URL = "http://127.0.0.1:8000";

    // Elementos da UI
    const loginView = document.getElementById("login-view");
    const registerView = document.getElementById("register-view");
    const dashboardView = document.getElementById("dashboard-view");

    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
    const addPetForm = document.getElementById("add-pet-form");
    
    const showRegisterLink = document.getElementById("show-register");
    const showLoginLink = document.getElementById("show-login");
    const logoutButton = document.getElementById("logout-button");

    const loginError = document.getElementById("login-error");
    const registerError = document.getElementById("register-error");
    const petSuccessMsg = document.getElementById("pet-success");
    const userNameSpan = document.getElementById("user-name");
    const myPetsList = document.getElementById("my-pets-list");

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
    
    logoutButton.addEventListener("click", () => {
        localStorage.removeItem("petIdToken");
        showView("login-view");
        myPetsList.innerHTML = ""; // Limpa a lista de pets ao sair
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
        // O backend espera 'username' e 'password' no formato de formulário para o login
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
    // LÓGICA DO DASHBOARD (PETS)
    // =================================================================
    
    async function navigateToDashboard() {
        const token = localStorage.getItem("petIdToken");
        if (!token) return; // Se não tem token, não faz nada
        
        // Simulação de busca do nome do usuário. Em um app real, você teria um endpoint /users/me
        // Por agora, vamos apenas mostrar o dashboard.
        // const decodedToken = JSON.parse(atob(token.split('.')[1]));
        // userNameSpan.textContent = decodedToken.sub; // Mostra o email por enquanto

        showView("dashboard-view");
        await fetchMyPets();
    }

    addPetForm.addEventListener("submit", async(e) => {
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
                await fetchMyPets(); // Atualiza a lista de pets
            } else {
                const errorData = await response.json();
                alert(`Erro ao cadastrar pet: ${errorData.detail}`);
            }

        } catch(error) {
            alert("Erro de conexão ao cadastrar pet.");
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
                myPetsList.innerHTML = ""; // Limpa a lista atual
                if (pets.length === 0) {
                    myPetsList.innerHTML = "<p>Você ainda não tem pets cadastrados.</p>";
                } else {
                    pets.forEach(pet => {
                        const petElement = document.createElement("div");
                        petElement.className = "pet-item";
                         const imageUrl = `${API_URL}/static/${pet.foto_url}`;
                        // NOTA: A foto não vai funcionar ainda porque o backend não a está servindo estaticamente.
                        // Veremos isso nos próximos passos.
                        petElement.innerHTML = `
                            <img src="${imageUrl}" alt="Foto de ${pet.nome}">
                            <div>
                                <h3>${pet.nome}</h3>
                                <p>${pet.especie} - ${pet.raca}</p>
                            </div>
                        `;
                        myPetsList.appendChild(petElement);
                    });
                }
            }
        } catch (error) {
            myPetsList.innerHTML = "<p>Erro ao carregar seus pets.</p>";
        }
    }


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