// nav.js - Barra de navegação compartilhada (Dashboard, Dispositivos, Alertas, Perfil, Sair)
// Depende de auth.js (logout) - carregado antes deste script
// Uso: cada página protegida tem <div id="nav-container"></div> e chama renderNav('dashboard') etc.

// Renderiza a barra de navegação no container #nav-container
// activePage: 'dashboard' | 'devices' | 'alerts' | 'profile' - destaca o link ativo
function renderNav(activePage) {
    const links = [
        { page: 'dashboard', label: 'Dashboard', href: 'dashboard.html' },
        { page: 'devices', label: 'Dispositivos', href: 'devices.html' },
        { page: 'alerts', label: 'Alertas', href: 'alerts.html' },
        { page: 'profile', label: 'Perfil', href: 'profile.html' }
    ];

    const linkItems = links.map(function(link) {
        const activeClass = link.page === activePage ? 'font-bold text-blue-600' : 'text-gray-700 hover:text-blue-600';
        return '<a href="' + link.href + '" class="' + activeClass + ' px-3 py-2 rounded">' + link.label + '</a>';
    }).join('');

    const navHtml =
        '<nav class="bg-white shadow">' +
            '<div class="flex items-center justify-between px-4 py-3">' +
                '<a href="dashboard.html" class="text-xl font-bold text-blue-600">Fungu</a>' +
                '<div class="flex items-center space-x-2">' +
                    linkItems +
                    '<button onclick="logout()" class="text-gray-700 hover:text-blue-600 px-3 py-2 rounded">Sair</button>' +
                '</div>' +
            '</div>' +
        '</nav>';

    document.getElementById('nav-container').innerHTML = navHtml;
}
