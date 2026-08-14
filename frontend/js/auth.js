// auth.js - Autenticação (login, register, logout, guards)
// Depende de api.js (apiPost, isLoggedIn, setTokens, clearTokens) - carregado antes deste script

// Guarda de rota protegida: redireciona para login.html se não autenticado
function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = 'login.html';
    }
}

// Realiza login via POST /auth/login e armazena os tokens
async function login(email, password) {
    try {
        const response = await apiPost('/auth/login', { email, password });
        setTokens(response.access_token, response.refresh_token);
        return true;
    } catch (error) {
        return false;
    }
}

// Registra um novo usuário via POST /users/register
async function register(email, password) {
    try {
        await apiPost('/users/register', { email, password });
        return true;
    } catch (error) {
        return false;
    }
}

// Encerra a sessão: limpa os tokens e redireciona para login.html
function logout() {
    clearTokens();
    window.location.href = 'login.html';
}

// Usado em login.html/register.html: pula para o dashboard se já autenticado
function redirectIfLoggedIn() {
    if (isLoggedIn()) {
        window.location.href = 'dashboard.html';
    }
}
