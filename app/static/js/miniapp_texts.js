// miniapp_texts.js - Mini App Texts management page

let allTextsData = {};   // { code: { id, name, code, is_default, translations: { key: { id, value, category } } } }
let allLanguages = [];
let activeLanguageId = null;
let activeLanguageCode = null;
let pendingChanges = {};  // { translationId: newValue }

document.addEventListener('DOMContentLoaded', function () {
    loadDefaultTexts().then(() => loadAllTexts());
    document.getElementById('searchInput').addEventListener('input', renderTable);
    document.getElementById('categoryFilter').addEventListener('change', renderTable);
});

async function loadDefaultTexts() {
    try {
        const response = await fetch('/api/languages/default-texts');
        if (response.ok) {
            const data = await response.json();
            window._defaultTexts = data.translations || {};
        }
    } catch (_) {
        window._defaultTexts = {};
    }
}

async function loadAllTexts() {
    try {
        const response = await fetch('/api/languages/all-texts');
        if (!response.ok) throw new Error('Failed to load texts');
        allTextsData = await response.json();

        // Build sorted language list (default first)
        allLanguages = Object.values(allTextsData).sort((a, b) => {
            if (a.is_default) return -1;
            if (b.is_default) return 1;
            return a.name.localeCompare(b.name);
        });

        renderTabs();
        populateCategoryFilter();

        if (allLanguages.length > 0) {
            selectLanguage(allLanguages[0].id, allLanguages[0].code);
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Failed to load mini app texts', 'danger');
    }
}

function renderTabs() {
    const container = document.getElementById('languageTabsContainer');
    if (allLanguages.length === 0) {
        container.innerHTML = '<p class="text-muted">No languages found. <a href="/admin/languages">Add languages</a> first.</p>';
        return;
    }

    let html = '<ul class="nav nav-tabs">';
    allLanguages.forEach(lang => {
        const badge = lang.is_default ? ' <span class="badge bg-warning text-dark ms-1">default</span>' : '';
        const active = lang.id === activeLanguageId ? ' active' : '';
        html += `<li class="nav-item">
            <a class="nav-link${active}" href="#" data-lang-id="${lang.id}" data-lang-code="${lang.code}" onclick="selectLanguage(${lang.id}, '${lang.code}'); return false;">
                ${lang.name} <code class="ms-1">${lang.code}</code>${badge}
            </a>
        </li>`;
    });
    html += '</ul>';
    container.innerHTML = html;
}

function selectLanguage(langId, langCode) {
    if (pendingChanges && Object.keys(pendingChanges).length > 0) {
        if (!confirm('You have unsaved changes. Switch language anyway?')) return;
    }
    activeLanguageId = langId;
    activeLanguageCode = langCode;
    pendingChanges = {};

    // Update tabs using data attributes for reliable matching
    document.querySelectorAll('#languageTabsContainer .nav-link').forEach(el => {
        el.classList.toggle('active', parseInt(el.getAttribute('data-lang-id')) === langId);
    });

    const langInfo = allTextsData[langCode];
    document.getElementById('activeLanguageName').textContent = langInfo ? `${langInfo.name} (${langCode})` : langCode;

    // Enable buttons
    document.getElementById('generateDefaultsTabBtn').disabled = false;
    const atBtn = document.getElementById('autoTranslateTabBtn');
    atBtn.classList.remove('d-none');

    renderTable();
}

function getActiveTranslations() {
    if (!activeLanguageCode || !allTextsData[activeLanguageCode]) return {};
    return allTextsData[activeLanguageCode].translations || {};
}

function populateCategoryFilter() {
    const cats = new Set();
    Object.values(allTextsData).forEach(lang => {
        Object.values(lang.translations || {}).forEach(t => {
            if (t.category) cats.add(t.category);
        });
    });
    const select = document.getElementById('categoryFilter');
    select.innerHTML = '<option value="">All Categories</option>' +
        [...cats].sort().map(c => `<option value="${c}">${c}</option>`).join('');
}

function renderTable() {
    const tbody = document.getElementById('textsTableBody');
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const categoryFilter = document.getElementById('categoryFilter').value;
    const translations = getActiveTranslations();

    // Get all keys: union of default keys and existing translations
    const defaultKeys = Object.keys(window._defaultTexts || {});
    const existingKeys = Object.keys(translations);
    const allKeys = [...new Set([...defaultKeys, ...existingKeys])].sort();

    if (allKeys.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center py-4 text-muted">No texts found. Click "Generate Defaults" to add default mini-app texts.</td></tr>';
        document.getElementById('rowCount').textContent = '';
        return;
    }

    let visible = 0;
    const rows = allKeys.map(key => {
        const trans = translations[key];
        const value = trans ? trans.value : '';
        const category = trans ? trans.category : 'general';
        const transId = trans ? trans.id : null;

        const matchesSearch = !searchTerm || key.toLowerCase().includes(searchTerm) || value.toLowerCase().includes(searchTerm);
        const matchesCategory = !categoryFilter || category === categoryFilter;

        if (!matchesSearch || !matchesCategory) return '';
        visible++;

        const escapedKey = key.replace(/"/g, '&quot;');
        const pendingValue = pendingChanges[transId] !== undefined ? pendingChanges[transId] : value;
        const isDirty = transId && pendingChanges[transId] !== undefined;

        return `<tr data-key="${escapedKey}" data-trans-id="${transId || ''}" data-category="${category}" ${isDirty ? 'class="table-warning"' : ''}>
            <td><code class="small">${key}</code></td>
            <td>
                <textarea class="form-control form-control-sm text-value" 
                          data-key="${escapedKey}" 
                          data-trans-id="${transId || ''}"
                          rows="2"
                          oninput="onTextChange(this)">${pendingValue}</textarea>
            </td>
            <td><span class="badge bg-info text-dark">${category}</span></td>
            <td>
                <button class="btn btn-sm btn-success" onclick="saveRowText('${escapedKey}')" title="Save">
                    <i class="bi bi-save"></i>
                </button>
                <button class="btn btn-sm btn-primary" onclick="openEditModal('${escapedKey}')" title="Edit in modal">
                    <i class="bi bi-pencil"></i>
                </button>
            </td>
        </tr>`;
    });

    tbody.innerHTML = rows.join('') || '<tr><td colspan="4" class="text-center py-3 text-muted">No matching texts found.</td></tr>';
    document.getElementById('rowCount').textContent = `${visible} of ${allKeys.length} texts`;
}

function onTextChange(textarea) {
    const transId = textarea.getAttribute('data-trans-id');
    if (transId) {
        pendingChanges[transId] = textarea.value;
        const row = textarea.closest('tr');
        if (row) row.classList.add('table-warning');
    }
}

async function saveRowText(key) {
    const translations = getActiveTranslations();
    const trans = translations[key];
    const textarea = document.querySelector(`textarea[data-key="${key}"]`);
    if (!textarea) return;

    const newValue = textarea.value;

    if (trans) {
        // Update existing
        try {
            const response = await fetch(`/api/languages/translations/${trans.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ value: newValue })
            });
            if (!response.ok) throw new Error('Failed to save');
            trans.value = newValue;
            delete pendingChanges[trans.id];
            const row = textarea.closest('tr');
            if (row) row.classList.remove('table-warning');
            showAlert('Saved', 'success');
        } catch (error) {
            showAlert('Failed to save: ' + error.message, 'danger');
        }
    } else {
        // Create new translation
        try {
            const response = await fetch('/api/languages/translations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    language_id: activeLanguageId,
                    key: key,
                    value: newValue,
                    category: 'general'
                })
            });
            if (!response.ok) throw new Error('Failed to create');
            const result = await response.json();
            allTextsData[activeLanguageCode].translations[key] = { id: result.id, value: newValue, category: 'general' };
            renderTable();
            showAlert('Saved', 'success');
        } catch (error) {
            showAlert('Failed to save: ' + error.message, 'danger');
        }
    }
}

async function saveAllChanges() {
    const translations = getActiveTranslations();
    const toUpdate = {};

    document.querySelectorAll('.text-value').forEach(textarea => {
        const key = textarea.getAttribute('data-key');
        const trans = translations[key];
        const originalValue = trans ? trans.value : '';
        if (textarea.value !== originalValue) {
            toUpdate[key] = textarea.value;
        }
    });

    if (Object.keys(toUpdate).length === 0) {
        showAlert('No changes to save', 'info');
        return;
    }

    try {
        const response = await fetch(`/api/languages/translations/bulk?language_id=${activeLanguageId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(toUpdate)
        });
        if (!response.ok) throw new Error('Failed to save');
        const result = await response.json();
        showAlert(result.message, 'success');
        pendingChanges = {};
        // Refresh data
        await loadAllTexts();
        selectLanguage(activeLanguageId, activeLanguageCode);
    } catch (error) {
        showAlert('Failed to save: ' + error.message, 'danger');
    }
}

function openEditModal(key) {
    const translations = getActiveTranslations();
    const trans = translations[key];
    document.getElementById('editTextKey').value = key;
    document.getElementById('editTextValue').value = trans ? trans.value : '';
    document.getElementById('editTextTranslationId').value = trans ? trans.id : '';
    new bootstrap.Modal(document.getElementById('editTextModal')).show();
}

async function saveEditedText() {
    const key = document.getElementById('editTextKey').value;
    const newValue = document.getElementById('editTextValue').value;
    const transId = document.getElementById('editTextTranslationId').value;

    const translations = getActiveTranslations();
    const trans = translations[key];

    try {
        if (trans || transId) {
            const id = transId || trans.id;
            const response = await fetch(`/api/languages/translations/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ value: newValue })
            });
            if (!response.ok) throw new Error('Failed to save');
            if (trans) trans.value = newValue;
        } else {
            const response = await fetch('/api/languages/translations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    language_id: activeLanguageId,
                    key: key,
                    value: newValue,
                    category: 'general'
                })
            });
            if (!response.ok) throw new Error('Failed to create');
            const result = await response.json();
            allTextsData[activeLanguageCode].translations[key] = { id: result.id, value: newValue, category: 'general' };
        }
        bootstrap.Modal.getInstance(document.getElementById('editTextModal')).hide();
        showAlert('Saved', 'success');
        renderTable();
    } catch (error) {
        showAlert('Failed to save: ' + error.message, 'danger');
    }
}

async function generateDefaultsForActive() {
    if (!activeLanguageId) return;
    if (!confirm('Add missing default mini-app texts to this language? Existing translations will not be changed.')) return;

    try {
        const response = await fetch(`/api/languages/${activeLanguageId}/generate-defaults`, { method: 'POST' });
        if (!response.ok) throw new Error('Failed');
        const result = await response.json();
        showAlert(result.message, 'success');
        await loadAllTexts();
        selectLanguage(activeLanguageId, activeLanguageCode);
    } catch (error) {
        showAlert('Failed: ' + error.message, 'danger');
    }
}

async function generateDefaultsAll() {
    if (!confirm('Add missing default texts to ALL languages? Existing translations will not be changed.')) return;

    let total = 0;
    for (const lang of allLanguages) {
        try {
            const response = await fetch(`/api/languages/${lang.id}/generate-defaults`, { method: 'POST' });
            if (response.ok) {
                const result = await response.json();
                total += result.added || 0;
            }
        } catch (_) {}
    }
    showAlert(`Added ${total} default translations across all languages`, 'success');
    await loadAllTexts();
    if (activeLanguageId && activeLanguageCode) {
        selectLanguage(activeLanguageId, activeLanguageCode);
    }
}

function showAutoTranslateModal() {
    // Populate source language select (exclude active language)
    const select = document.getElementById('autoTranslateSource');
    const options = allLanguages
        .filter(l => l.id !== activeLanguageId)
        .map(l => `<option value="${l.id}">${l.name} (${l.code})</option>`)
        .join('');
    select.innerHTML = options || '<option value="">No other languages available</option>';
    new bootstrap.Modal(document.getElementById('autoTranslateModal')).show();
}

async function runAutoTranslate() {
    const sourceId = document.getElementById('autoTranslateSource').value;
    if (!sourceId) {
        showAlert('Please select a source language', 'warning');
        return;
    }
    const overwrite = document.getElementById('autoTranslateOverwrite').checked;
    const btn = document.getElementById('autoTranslateBtn');
    const progress = document.getElementById('autoTranslateProgress');

    btn.disabled = true;
    progress.classList.remove('d-none');

    try {
        const response = await fetch(
            `/api/languages/${activeLanguageId}/auto-translate?source_language_id=${sourceId}&overwrite=${overwrite}`,
            { method: 'POST' }
        );
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Auto-translate failed');
        }
        const result = await response.json();
        bootstrap.Modal.getInstance(document.getElementById('autoTranslateModal')).hide();
        showAlert(`${result.message}${result.failed > 0 ? ` (${result.failed} failed)` : ''}`, 'success');
        await loadAllTexts();
        selectLanguage(activeLanguageId, activeLanguageCode);
    } catch (error) {
        showAlert(error.message, 'danger');
    } finally {
        btn.disabled = false;
        progress.classList.add('d-none');
    }
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    setTimeout(() => alertDiv.remove(), 5000);
}
