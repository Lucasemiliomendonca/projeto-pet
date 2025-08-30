import { useState } from 'react';
import Login from './components/Login';

function App() {
  // Estado para guardar o token. Começa como null (usuário não logado)
  const [token, setToken] = useState(null);

  // Função que será passada para o componente Login
  const handleLoginSuccess = (receivedToken) => {
    // 1. Guarda o token no estado do App
    setToken(receivedToken);
    // 2. Guarda o token no localStorage para "lembrar" do login
    localStorage.setItem("petIdToken", receivedToken);
  };

  return (
    <div>
      {/* Aqui está a LÓGICA DE EXIBIÇÃO: */}
      {!token ? (
        // Se NÃO (!) houver token no estado, mostre o componente de Login
        <Login onLoginSuccess={handleLoginSuccess} />
      ) : (
        // Se HOUVER token, mostre o Dashboard (por enquanto, só uma mensagem)
        <div>
          <h1>LOGADO COM SUCESSO!</h1>
          <p>Bem-vindo ao Dashboard!</p>
        </div>
      )}
    </div>
  )
}

export default App;