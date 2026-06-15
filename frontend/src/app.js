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

// Initialize Application Context Lifecycle
document.addEventListener('DOMContentLoaded', fetchEntries);
diaryForm.addEventListener('submit', handleFormSubmit);
cancelBtn.addEventListener('click', resetFormState);

// VG UX Error Display Routine
function displayError(message) {
    errorBanner.textContent = `Fel: ${message}`;
    errorBanner.style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function clearError() {
    errorBanner.style.display = 'none';
    errorBanner.textContent = '';
}

// REST GET Request Operation
async function fetchEntries() {
    try {
        const response = await fetch(API_BASE_URL);
        if (!response.ok) throw new Error('Kunde inte hämta dagboksanteckningar från servern.');
        
        const entries = await response.json();
        renderEntries(entries);
        clearError();
    } catch (error) {
        displayError(error.message);
        entriesContainer.innerHTML = '<p class="danger-text">Kunde inte ladda inlägg. Kontrollera att backend körs.</p>';
    }
}

// Render Engine Mapping
function renderEntries(entries) {
    if (entries.length === 0) {
        entriesContainer.innerHTML = '<p>Inga dagboksanteckningar hittades. Skriv ditt första inlägg till vänster!</p>';
        return;
    }

    entriesContainer.innerHTML = entries.map(entry => {
        const dateStr = new Date(entry.created_at).toLocaleString('sv-SE', {
            dateStyle: 'short',
            timeStyle: 'short'
        });
        
        return `
            <div class="diary-card" id="entry-${entry.id}">
                <h3>${escapeHTML(entry.title)}</h3>
                <div class="diary-meta">
                    <span><strong>Kategori:</strong> ${escapeHTML(entry.category)}</span> | 
                    <span><strong>Skapad:</strong> ${dateStr}</span>
                </div>
                <p class="diary-body">${escapeHTML(entry.content).replace(/\n/g, '<br>')}</p>
                <div class="diary-actions">
                    <button onclick="populateEditForm(${entry.id}, '${escapeQuotes(entry.title)}', '${escapeQuotes(entry.category)}', '${escapeQuotes(entry.content)}')" class="btn btn-secondary">Redigera</button>
                    <button onclick="deleteEntry(${entry.id})" class="btn btn-danger">Radera</button>
                </div>
            </div>
        `;
    }).join('');
}

// REST POST / PUT Event Handler
async function handleFormSubmit(e) {
    e.preventDefault();
    clearError();

    const payload = {
        title: titleInput.value.trim(),
        category: categoryInput.value.trim(),
        content: contentInput.value.trim()
    };

    // UI Client Side Input Guard Validation
    if (!payload.title || !payload.category || !payload.content) {
        displayError("Alla fält måste fyllas i ordentligt.");
        return;
    }

    const url = isEditing ? `${API_BASE_URL}/${entryIdInput.value}` : API_BASE_URL;
    const method = isEditing ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'Ett fel uppstod vid kommunikation med API.');
        }

        resetFormState();
        await fetchEntries();
    } catch (error) {
        displayError(error.message);
    }
}

// REST DELETE Request Protocol
async function deleteEntry(id) {
    clearError();
    
    // VG UX Criterion: Intercept with Explicit Window Affirmative Confirmation Gate
    const confirmationGate = window.confirm("Är du helt säker på att du vill radera denna dagboksanteckning?");
    if (!confirmationGate) return;

    try {
        const response = await fetch(`${API_BASE_URL}/${id}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Misslyckades med att radera inlägget från servern.');
        
        await fetchEntries();
    } catch (error) {
        displayError(error.message);
    }
}

// Form State Management Utility Blocks
function populateEditForm(id, title, category, content) {
    isEditing = true;
    formTitle.textContent = "Redigera anteckning";
    entryIdInput.value = id;
    titleInput.value = title;
    categoryInput.value = category;
    contentInput.value = content;
    cancelBtn.style.display = 'inline-block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function resetFormState() {
    isEditing = false;
    formTitle.textContent = "Skapa ny anteckning";
    diaryForm.reset();
    entryIdInput.value = '';
    cancelBtn.style.display = 'none';
}

// XSS Prevention Sanitizers
function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, tag => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
    }[tag] || tag));
}

function escapeQuotes(str) {
    return str.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '&quot;').replace(/\n/g, '\\n');
}
