// profile.js - Página de perfil (informações do usuário, contatos, logout)
// Depende de api.js (apiGet, apiPatch) e auth.js (requireAuth, logout) - carregados antes deste script

// Carrega os dados do perfil do usuário via GET /users/me
async function loadProfile() {
    try {
        const user = await apiGet('/users/me');
        document.getElementById('user-id').textContent = user.id;
        document.getElementById('user-email').textContent = user.email;
        document.getElementById('telegram-chat-id').value = user.telegram_chat_id || '';
        document.getElementById('alert-email').value = user.alert_email || '';
    } catch (error) {
        const msg = document.getElementById('contacts-msg');
        msg.textContent = 'Erro ao carregar perfil';
        msg.classList.remove('hidden');
        msg.classList.add('text-red-500');
    }
}

// Salva os contatos via PATCH /users/contacts
async function saveContacts() {
    const msg = document.getElementById('contacts-msg');
    msg.classList.add('hidden');

    const telegram_chat_id = document.getElementById('telegram-chat-id').value;
    const alert_email = document.getElementById('alert-email').value;

    try {
        await apiPatch('/users/contacts', { telegram_chat_id, alert_email });
        msg.textContent = 'Contatos atualizados com sucesso';
        msg.classList.remove('hidden');
        msg.classList.add('text-green-500');
    } catch (error) {
        msg.textContent = error.message || 'Erro ao salvar contatos';
        msg.classList.remove('hidden');
        msg.classList.add('text-red-500');
    }
}

// Encerra a sessão e redireciona para login.html
function handleLogout() {
    logout();
}

// Inicialização da página
requireAuth();
renderNav('profile');
loadProfile();

document.getElementById('save-contacts-btn').addEventListener('click', saveContacts);
document.getElementById('logout-btn').addEventListener('click', handleLogout);
