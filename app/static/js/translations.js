// translations.js - Translations editor JavaScript

let translations = [];
let categories = [];
let languageId = null;
let languageInfo = null;

// Load translations on page load
document.addEventListener('DOMContentLoaded', function() {
    languageId = parseInt(document.getElementById('currentLanguageId').value);
    if (languageId) {
        loadLanguage();
        loadTranslations();
        loadCategories();
    }
    
    // Setup search
    document.getElementById('searchInput').addEventListener('input', filterTranslations);
    document.getElementById('categoryFilter').addEventListener('change', filterTranslations);
});

async function loadLanguage() {
    try {
        const response = await fetch(`/api/languages/${languageId}`);
        if (!response.ok) {
            throw new Error('Failed to load language');
        }
        languageInfo = await response.json();
        document.getElementById('languageName').textContent = `${languageInfo.name} (${languageInfo.code})`;
    } catch (error) {
        console.error('Error loading language:', error);
        showAlert('Failed to load language info', 'danger');
    }
}

async function loadTranslations() {
    try {
        const response = await fetch(`/api/languages/${languageId}/translations`);
        if (!response.ok) {
            throw new Error('Failed to load translations');
        }
        translations = await response.json();
        renderTranslationsTable();
    } catch (error) {
        console.error('Error loading translations:', error);
        showAlert('Failed to load translations', 'danger');
    }
}

async function loadCategories() {
    try {
        const response = await fetch(`/api/languages/${languageId}/categories`);
        if (!response.ok) {
            throw new Error('Failed to load categories');
        }
        categories = await response.json();
        renderCategoryFilter();
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

function renderCategoryFilter() {
    const select = document.getElementById('categoryFilter');
    select.innerHTML = '<option value="">All Categories</option>' +
        categories.map(cat => `<option value="${cat}">${cat}</option>`).join('');
}

function renderTranslationsTable() {
    const tbody = document.getElementById('translationsTableBody');
    
    if (translations.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center">No translations found</td></tr>';
        return;
    }
    
    tbody.innerHTML = translations.map(trans => `
        <tr data-id="${trans.id}" data-category="${trans.category}">
            <td><code>${trans.key}</code></td>
            <td>
                <textarea class="form-control form-control-sm translation-value" 
                          data-id="${trans.id}" 
                          rows="2">${trans.value}</textarea>
            </td>
            <td><span class="badge bg-info">${trans.category}</span></td>
            <td>
                <button class="btn btn-sm btn-success" onclick="saveTranslation(${trans.id})">
                    <i class="bi bi-save"></i>
                </button>
                <button class="btn btn-sm btn-primary" onclick="editTranslationModal(${trans.id})">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteTranslation(${trans.id})">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

function filterTranslations() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const categoryFilter = document.getElementById('categoryFilter').value;
    
    const rows = document.querySelectorAll('#translationsTableBody tr');
    
    rows.forEach(row => {
        const key = row.querySelector('code')?.textContent.toLowerCase() || '';
        const value = row.querySelector('textarea')?.value.toLowerCase() || '';
        const category = row.getAttribute('data-category') || '';
        
        const matchesSearch = key.includes(searchTerm) || value.includes(searchTerm);
        const matchesCategory = !categoryFilter || category === categoryFilter;
        
        if (matchesSearch && matchesCategory) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

async function addTranslation() {
    const form = document.getElementById('addTranslationForm');
    const formData = new FormData(form);
    
    const translationData = {
        language_id: languageId,
        key: formData.get('key'),
        value: formData.get('value'),
        category: formData.get('category') || 'general'
    };
    
    try {
        const response = await fetch('/api/languages/translations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(translationData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to add translation');
        }
        
        showAlert('Translation added successfully', 'success');
        bootstrap.Modal.getInstance(document.getElementById('addTranslationModal')).hide();
        form.reset();
        loadTranslations();
        loadCategories();
    } catch (error) {
        console.error('Error adding translation:', error);
        showAlert(error.message, 'danger');
    }
}

function editTranslationModal(translationId) {
    const translation = translations.find(t => t.id === translationId);
    if (!translation) return;
    
    document.getElementById('editTranslationId').value = translation.id;
    document.getElementById('editTranslationKey').value = translation.key;
    document.getElementById('editTranslationValue').value = translation.value;
    document.getElementById('editTranslationCategory').value = translation.category;
    
    const modal = new bootstrap.Modal(document.getElementById('editTranslationModal'));
    modal.show();
}

async function updateTranslation() {
    const translationId = document.getElementById('editTranslationId').value;
    const form = document.getElementById('editTranslationForm');
    const formData = new FormData(form);
    
    const translationData = {
        value: formData.get('value'),
        category: formData.get('category')
    };
    
    try {
        const response = await fetch(`/api/languages/translations/${translationId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(translationData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to update translation');
        }
        
        showAlert('Translation updated successfully', 'success');
        bootstrap.Modal.getInstance(document.getElementById('editTranslationModal')).hide();
        loadTranslations();
        loadCategories();
    } catch (error) {
        console.error('Error updating translation:', error);
        showAlert(error.message, 'danger');
    }
}

async function saveTranslation(translationId) {
    const textarea = document.querySelector(`textarea[data-id="${translationId}"]`);
    const newValue = textarea.value;
    
    try {
        const response = await fetch(`/api/languages/translations/${translationId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ value: newValue })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to save translation');
        }
        
        showAlert('Translation saved', 'success');
        
        // Update the translation in memory
        const translation = translations.find(t => t.id === translationId);
        if (translation) {
            translation.value = newValue;
        }
    } catch (error) {
        console.error('Error saving translation:', error);
        showAlert(error.message, 'danger');
    }
}

async function saveAllChanges() {
    const textareas = document.querySelectorAll('.translation-value');
    const changes = {};
    
    textareas.forEach(textarea => {
        const translationId = parseInt(textarea.getAttribute('data-id'));
        const translation = translations.find(t => t.id === translationId);
        if (translation && textarea.value !== translation.value) {
            changes[translation.key] = textarea.value;
        }
    });
    
    if (Object.keys(changes).length === 0) {
        showAlert('No changes to save', 'info');
        return;
    }
    
    try {
        const response = await fetch(`/api/languages/translations/bulk?language_id=${languageId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(changes)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to save changes');
        }
        
        showAlert(`Saved ${Object.keys(changes).length} translations`, 'success');
        loadTranslations();
    } catch (error) {
        console.error('Error saving changes:', error);
        showAlert(error.message, 'danger');
    }
}

async function deleteTranslation(translationId) {
    if (!confirm('Are you sure you want to delete this translation?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/languages/translations/${translationId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to delete translation');
        }
        
        showAlert('Translation deleted successfully', 'success');
        loadTranslations();
        loadCategories();
    } catch (error) {
        console.error('Error deleting translation:', error);
        showAlert(error.message, 'danger');
    }
}

async function exportLanguage() {
    if (!languageInfo) return;
    
    try {
        const response = await fetch(`/api/languages/export/${languageInfo.code}`);
        if (!response.ok) {
            throw new Error('Failed to export language');
        }
        
        const data = await response.json();
        
        // Create download link
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `language_${languageInfo.code}.json`;
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
