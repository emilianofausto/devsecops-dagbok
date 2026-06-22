// Initialize Auth0 globally for HTML onclick handlers
window.auth0Client = null;

const configureAuth0 = async () => {
    // Defensive check to avoid ReferenceError if the Auth0 CDN takes time to parse
    if (typeof auth0 === 'undefined') {
        console.warn("Auth0 SDK is not available yet. Retrying...");
        await new Promise(resolve => setTimeout(resolve, 100));
        return configureAuth0();
    }

    window.auth0Client = await auth0.createAuth0Client({
        domain: 'floki-security.us.auth0.com',
        clientId: 'NQXqkUzGh1Mh1X3NXFE4OCbR9XlYp8TU',
        authorizationParams: {
            redirect_uri: window.location.origin,
            audience: 'https://devsecops-dagbok.onrender.com'
        }
    });

    // Handle the redirect callback
    if (window.location.search.includes("code=") && window.location.search.includes("state=")) {
        await window.auth0Client.handleRedirectCallback();
        window.history.replaceState({}, document.title, window.location.pathname);
    }
};

// UI Toggling Helper
const updateAuthUI = async () => {
    const isAuthenticated = await window.auth0Client.isAuthenticated();
    document.getElementById('view-unauthenticated').style.display = isAuthenticated ? 'none' : 'block';
    document.getElementById('view-authenticated').style.display = isAuthenticated ? 'block' : 'none';

    if (isAuthenticated) {
        const user = await window.auth0Client.getUser();
        document.getElementById('user-email').textContent = user.email;
    }
};

// Call this on app load
window.addEventListener("load", async () => {
    await configureAuth0();

    const isAuthenticated = await window.auth0Client.isAuthenticated();

    // Force automatic redirection if no active session exists
    if (!isAuthenticated) {
        await window.auth0Client.loginWithRedirect();
        return;
    }

    await updateAuthUI();
    await fetchEntries(); // Start fetching data
});

const API_BASE_URL = '/api/entries';

// DOM Selectors
const diaryForm = document.getElementById('diary-form');
const entryIdInput = document.getElementById('entry-id');
const titleInput = document.getElementById('title');
const categoryInput = document.getElementById('category');
const contentInput = document.getElementById('content');
const entriesContainer = document.getElementById('entries-container');
const errorBanner = document.getElementById('error-banner');
const formTitle = document.getElementById('form-title');
const cancelBtn = document.getElementById('cancel-btn');

let isEditing = false;

// Initialize Event Listeners
diaryForm.addEventListener('submit', handleFormSubmit);
cancelBtn.addEventListener('click', resetFormState);

function displayError(message) {
    errorBanner.textContent = `Fel: ${message}`;
    errorBanner.style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function clearError() {
    errorBanner.style.display = 'none';
    errorBanner.textContent = '';
}

// REST GET with Auth Token
async function fetchEntries() {
    try {
        const token = await window.auth0Client.getTokenSilently();
        const response = await fetch(API_BASE_URL, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('Kunde inte hämta dagboksanteckningar.');

        const entries = await response.json();
        renderEntries(entries);
        clearError();
    } catch (error) {
        displayError(error.message);
        entriesContainer.innerHTML = '<p class="danger-text">Kunde inte ladda inlägg. Logga in för att se dina anteckningar.</p>';
    }
}

function renderEntries(entries) {
    if (entries.length === 0) {
        entriesContainer.innerHTML = '<p>Inga dagboksanteckningar hittades.</p>';
        return;
    }

    entriesContainer.innerHTML = entries.map(entry => `
        <div class="diary-card" id="entry-${entry.id}">
            <h3>${escapeHTML(entry.title)}</h3>
            <p>${escapeHTML(entry.content)}</p>
            <div class="diary-actions">
                <button onclick="populateEditForm(${entry.id}, '${escapeQuotes(entry.title)}', '${escapeQuotes(entry.category)}', '${escapeQuotes(entry.content)}')" class="btn btn-secondary">Redigera</button>
                <button onclick="deleteEntry(${entry.id})" class="btn btn-danger">Radera</button>
            </div>
        </div>
    `).join('');
}

// REST Mutations with Auth Token
async function handleFormSubmit(e) {
    e.preventDefault();
    const token = await window.auth0Client.getTokenSilently();
    const url = isEditing ? `${API_BASE_URL}/${entryIdInput.value}` : API_BASE_URL;
    const method = isEditing ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                title: titleInput.value.trim(),
                category: categoryInput.value.trim(),
                content: contentInput.value.trim()
            })
        });
        if (!response.ok) throw new Error('Misslyckades med att spara.');
        resetFormState();
        await fetchEntries();
    } catch (error) { displayError(error.message); }
}

async function deleteEntry(id) {
    const token = await window.auth0Client.getTokenSilently();
    if (!window.confirm("Radera?")) return;

    try {
        await fetch(`${API_BASE_URL}/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        await fetchEntries();
    } catch (error) { displayError(error.message); }
}

function resetFormState() {
    isEditing = false;
    diaryForm.reset();
    formTitle.textContent = 'Skapa ny anteckning'; // Reset the form header back to default text
    cancelBtn.style.display = 'none';
}

function escapeHTML(str) { return str.replace(/[&<>'"]/g, t => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '\'': '&#39;', '"': '&quot;' }[t])); }
function escapeQuotes(str) {
    // 1. Escape the backslash first
    // 2. Escape the single quote
    // 3. Escape the double quote
    return str
        .replace(/\\/g, '\\\\')
        .replace(/'/g, "\\'")
        .replace(/"/g, '&quot;');
}

window.populateEditForm = function (id, title, category, content) {
    isEditing = true;
    formTitle.textContent = 'Redigera anteckning';
    entryIdInput.value = id;
    titleInput.value = title;
    categoryInput.value = category;
    contentInput.value = content;
    cancelBtn.style.display = 'inline-block';
};
