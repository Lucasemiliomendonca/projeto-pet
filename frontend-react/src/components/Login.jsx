import { useState } from 'react';
import './Login.css';

// O componente agora recebe uma "prop" chamada onLoginSuccess
function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(''); // Um estado para guardar mensagens de erro

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); // Limpa erros anteriores

    // Prepara os dados para enviar para a API (igual ao JS puro)
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    try {
      const response = await fetch("http://127.0.0.1:8000/token", {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        // AVISO DE SUCESSO! Chama a função que o App.jsx nos passou
        onLoginSuccess(data.access_token);
      } else {
        // Se deu erro, atualiza o estado de erro
        setError("Email ou senha incorretos.");
      }
    } catch (err) {
      setError("Falha na conexão com o servidor.");
    }
  }

  return (
    <main>
      <div className="card">
        <h2>Login</h2>
        <form onSubmit={handleSubmit}>
          <input 
            type="email" 
            placeholder="Email" 
            required 
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input 
            type="password" 
            placeholder="Senha" 
            required 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button type="submit">Entrar</button>
        </form>
        {/* Exibe a mensagem de erro, se houver alguma */}
        {error && <p className="error-message">{error}</p>}
        <a href="#">Não tem uma conta? Cadastre-se</a>
      </div>
    </main>
  );
}

export default Login;