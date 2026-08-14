// api.js - API client module with JWT token management
// Vanilla JS, loaded via script tags (no ES6 modules)

const API_BASE = '';

function getAccessToken() {
    return localStorage.getItem('access_token');
}

function getRefreshToken() {
    return localStorage.getItem('refresh_token');
}

function setTokens(accessToken, refreshToken) {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
}

function clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
}

function isLoggedIn() {
    return !!getAccessToken();
}

async function refreshAccessToken() {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
        return false;
    }
    const response = await fetch('/auth/refresh?token=' + refreshToken);
    if (response.status === 200) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        return true;
    }
    return false;
}

async function apiRequest(method, path, body) {
    const headers = {};
    const accessToken = getAccessToken();
    if (accessToken) {
        headers['Authorization'] = 'Bearer ' + accessToken;
    }

    let jsonBody;
    if ((method === 'POST' || method === 'PATCH') && body) {
        headers['Content-Type'] = 'application/json';
        jsonBody = JSON.stringify(body);
    }

    let response = await fetch(path, {
        method: method,
        headers: headers,
        body: jsonBody
    });

    if (response.status === 401) {
        const refreshed = await refreshAccessToken();
        if (refreshed) {
            headers['Authorization'] = 'Bearer ' + getAccessToken();
            response = await fetch(path, {
                method: method,
                headers: headers,
                body: jsonBody
            });
        } else {
            clearTokens();
            window.location.href = 'login.html';
            throw new Error('Sessão expirada');
        }
    }

    if (!response.ok) {
        let errorMessage = 'Erro na requisição';
        try {
            const errorData = await response.json();
            if (errorData.detail) {
                errorMessage = errorData.detail;
            }
        } catch (e) {
            // response body is not JSON, keep default message
        }
        throw new Error(errorMessage);
    }

    return response.json();
}

async function apiGet(path) {
    return apiRequest('GET', path);
}

async function apiPost(path, body) {
    return apiRequest('POST', path, body);
}

async function apiPatch(path, body) {
    return apiRequest('PATCH', path, body);
}
