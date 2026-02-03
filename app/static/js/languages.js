// languages.js - Language management JavaScript

let languages = [];

// Load languages on page load
document.addEventListener('DOMContentLoaded', function() {
    loadLanguages();
});

async function loadLanguages() {
    try {
        const response = await fetch('/api/languages/');
        if (!response.ok) {
            throw new Error('Failed to load languages');
        }
        languages = await response.json();
        renderLanguagesTable();
    } catch (error) {
        console.error('Error loading languages:', error);
        showAlert('Failed to load languages', 'danger');
    }
}

function renderLanguagesTable() {
    const tbody = document.getElementById('languagesTableBody');
    
    if (languages.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center">No languages found</td></tr>';
        return;
    }
    
    tbody.innerHTML = languages.map(lang => `
        <tr>
            <td>${lang.id}</td>
            <td><code>${lang.code}</code></td>
            <td>${lang.name}</td>
            <td>
                ${lang.is_active 
                    ? '<span class="badge bg-success">Active</span>' 
                    : '<span class="badge bg-secondary">Inactive</span>'}
            </td>
            <td>
                ${lang.is_default 
                    ? '<i class="bi bi-star-fill text-warning"></i> Default' 
                    : ''}
            </td>
            <td>
                <a href="/admin/translations/${lang.id}" class="btn btn-sm btn-info">
                    <i class="bi bi-pencil-square"></i> Edit Translations
                </a>
            </td>
            <td>${new Date(lang.created_at).toLocaleDateString()}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editLanguage(${lang.id})">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-success" onclick="exportLanguageData('${lang.code}')">
                    <i class="bi bi-download"></i>
                </button>
                ${!lang.is_default ? `
                    <button class="btn btn-sm btn-danger" onclick="deleteLanguage(${lang.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                ` : ''}
            </td>
        </tr>
    `).join('');
}

async function addLanguage() {
    const form = document.getElementById('addLanguageForm');
    const formData = new FormData(form);
    
    const languageData = {
        code: formData.get('code').toLowerCase(),
        name: formData.get('name'),
        is_active: formData.get('is_active') === 'on',
        is_default: formData.get('is_default') === 'on'
    };
    
    try {
        const response = await fetch('/api/languages/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(languageData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to add language');
        }
        
        showAlert('Language added successfully', 'success');
        bootstrap.Modal.getInstance(document.getElementById('addLanguageModal')).hide();
        form.reset();
        loadLanguages();
    } catch (error) {
        console.error('Error adding language:', error);
        showAlert(error.message, 'danger');
    }
}

function editLanguage(languageId) {
    const language = languages.find(l => l.id === languageId);
    if (!language) return;
    
    document.getElementById('editLanguageId').value = language.id;
    document.getElementById('editLanguageCode').value = language.code;
    document.getElementById('editLanguageName').value = language.name;
    document.getElementById('editLanguageActive').checked = language.is_active;
    document.getElementById('editLanguageDefault').checked = language.is_default;
    
    const modal = new bootstrap.Modal(document.getElementById('editLanguageModal'));
    modal.show();
}

async function updateLanguage() {
    const languageId = document.getElementById('editLanguageId').value;
    const form = document.getElementById('editLanguageForm');
    const formData = new FormData(form);
    
    const languageData = {
        code: formData.get('code').toLowerCase(),
        name: formData.get('name'),
        is_active: formData.get('is_active') === 'on',
        is_default: formData.get('is_default') === 'on'
    };
    
    try {
        const response = await fetch(`/api/languages/${languageId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(languageData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to update language');
        }
        
        showAlert('Language updated successfully', 'success');
        bootstrap.Modal.getInstance(document.getElementById('editLanguageModal')).hide();
        loadLanguages();
    } catch (error) {
        console.error('Error updating language:', error);
        showAlert(error.message, 'danger');
    }
}

async function deleteLanguage(languageId) {
    if (!confirm('Are you sure you want to delete this language? All translations will be deleted.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/languages/${languageId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to delete language');
        }
        
        showAlert('Language deleted successfully', 'success');
        loadLanguages();
    } catch (error) {
        console.error('Error deleting language:', error);
        showAlert(error.message, 'danger');
    }
}

async function exportLanguageData(languageCode) {
    try {
        const response = await fetch(`/api/languages/export/${languageCode}`);
        if (!response.ok) {
            throw new Error('Failed to export language');
        }
        
        const data = await response.json();
        
        // Create download link
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `language_${languageCode}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showAlert('Language exported successfully', 'success');
    } catch (error) {
        console.error('Error exporting language:', error);
        showAlert(error.message, 'danger');
    }
}

async function importLanguage() {
    const fileInput = document.getElementById('importFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showAlert('Please select a file to import', 'warning');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/languages/import-file', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to import language');
        }
        
        const result = await response.json();
        showAlert(result.message, 'success');
        bootstrap.Modal.getInstance(document.getElementById('importLanguageModal')).hide();
        fileInput.value = '';
        loadLanguages();
    } catch (error) {
        console.error('Error importing language:', error);
        showAlert(error.message, 'danger');
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
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}
