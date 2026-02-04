let availableLanguages = [];

async function loadLanguages() {
    try {
        const response = await fetch('/api/languages/');
        const data = await response.json();
        availableLanguages = data.languages || [];
    } catch (error) {
        console.error('Error loading languages:', error);
    }
}

async function loadCategories() {
    try {
        const response = await fetch('/api/categories/tree/all?include_translations=true');
        const data = await response.json();
        
        displayCategoryTree(data.tree);
        loadCategoryOptions();
    } catch (error) {
        console.error('Error loading categories:', error);
        showAlert('Error loading categories', 'danger');
    }
}

function displayCategoryTree(categories) {
    const container = document.getElementById('categories-tree');
    
    if (categories.length === 0) {
        container.innerHTML = '<p class="text-center text-muted">No categories found. Create one to get started.</p>';
        return;
    }
    
    container.innerHTML = '<ul class="list-group">' + 
        categories.map(cat => renderCategory(cat)).join('') + 
        '</ul>';
}

function renderCategory(category, level = 0) {
    const indent = level * 20;
    let html = `
        <li class="list-group-item" style="padding-left: ${20 + indent}px">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <i class="bi bi-folder${category.children && category.children.length > 0 ? '-fill' : ''}"></i>
                    <strong>${category.name}</strong>
                    ${category.label ? `<span class="badge bg-info ms-2">${category.label}</span>` : ''}
                    ${category.children && category.children.length > 0 ? `<span class="badge bg-secondary ms-2">${category.children.length} sub</span>` : ''}
                </div>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-primary" onclick="editCategory(${category.id})">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-danger" onclick="deleteCategory(${category.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        </li>
    `;
    
    if (category.children && category.children.length > 0) {
        html += category.children.map(child => renderCategory(child, level + 1)).join('');
    }
    
    return html;
}

async function loadCategoryOptions() {
    try {
        const response = await fetch('/api/categories/');
        const data = await response.json();
        
        const parentSelects = [
            document.getElementById('create-parent'),
            document.getElementById('edit-parent')
        ];
        
        parentSelects.forEach(select => {
            const currentValue = select.value;
            select.innerHTML = '<option value="">None (Root Category)</option>';
            
            data.categories.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat.id;
                option.textContent = cat.name;
                select.appendChild(option);
            });
            
            if (currentValue) {
                select.value = currentValue;
            }
        });
    } catch (error) {
        console.error('Error loading category options:', error);
    }
}

function renderTranslationInputs(containerId, translations = []) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = availableLanguages.map(lang => {
        const existingTrans = translations.find(t => t.language_id === lang.id);
        return `
            <div class="mb-2">
                <label class="form-label">${lang.name} (${lang.code.toUpperCase()})</label>
                <input type="text" 
                       class="form-control translation-input" 
                       data-language-id="${lang.id}"
                       value="${existingTrans ? existingTrans.name : ''}"
                       placeholder="Category name in ${lang.name}">
            </div>
        `;
    }).join('');
}

function getTranslationsFromInputs(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return [];
    
    const inputs = container.querySelectorAll('.translation-input');
    const translations = [];
    
    inputs.forEach(input => {
        const value = input.value.trim();
        if (value) {
            translations.push({
                language_id: parseInt(input.getAttribute('data-language-id')),
                name: value
            });
        }
    });
    
    return translations;
}

async function createCategory() {
    const name = document.getElementById('create-name').value.trim();
    if (!name) {
        showAlert('Please enter a category name', 'warning');
        return;
    }
    
    const label = document.getElementById('create-label').value.trim();
    const parentId = document.getElementById('create-parent').value;
    const translations = getTranslationsFromInputs('create-translations-container');
    
    const data = {
        name: name,
        label: label || null,
        parent_id: parentId ? parseInt(parentId) : null,
        translations: translations.length > 0 ? translations : null
    };
    
    try {
        const response = await fetch('/api/categories/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showAlert('Category created successfully', 'success');
            bootstrap.Modal.getInstance(document.getElementById('createCategoryModal')).hide();
            document.getElementById('create-category-form').reset();
            loadCategories();
        } else {
            showAlert('Error creating category', 'danger');
        }
    } catch (error) {
        console.error('Error creating category:', error);
        showAlert('Error creating category', 'danger');
    }
}

async function editCategory(categoryId) {
    try {
        const response = await fetch(`/api/categories/${categoryId}?include_translations=true`);
        const category = await response.json();
        
        document.getElementById('edit-category-id').value = category.id;
        document.getElementById('edit-name').value = category.name;
        document.getElementById('edit-label').value = category.label || '';
        document.getElementById('edit-parent').value = category.parent_id || '';
        
        // Render translation inputs with existing values
        renderTranslationInputs('edit-translations-container', category.translations || []);
        
        const modal = new bootstrap.Modal(document.getElementById('editCategoryModal'));
        modal.show();
    } catch (error) {
        console.error('Error loading category:', error);
        showAlert('Error loading category', 'danger');
    }
}

async function saveCategory() {
    const categoryId = document.getElementById('edit-category-id').value;
    const name = document.getElementById('edit-name').value.trim();
    
    if (!name) {
        showAlert('Please enter a category name', 'warning');
        return;
    }
    
    const label = document.getElementById('edit-label').value.trim();
    const parentId = document.getElementById('edit-parent').value;
    const translations = getTranslationsFromInputs('edit-translations-container');
    
    const data = {
        name: name,
        label: label || null,
        parent_id: parentId ? parseInt(parentId) : null,
        translations: translations.length > 0 ? translations : null
    };
    
    try {
        const response = await fetch(`/api/categories/${categoryId}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showAlert('Category updated successfully', 'success');
            bootstrap.Modal.getInstance(document.getElementById('editCategoryModal')).hide();
            loadCategories();
        } else {
            showAlert('Error updating category', 'danger');
        }
    } catch (error) {
        console.error('Error saving category:', error);
        showAlert('Error saving category', 'danger');
    }
}

async function deleteCategory(categoryId) {
    if (!confirm('Are you sure you want to delete this category? All subcategories will also be deleted.')) return;
    
    try {
        const response = await fetch(`/api/categories/${categoryId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showAlert('Category deleted successfully', 'success');
            loadCategories();
        } else {
            showAlert('Error deleting category', 'danger');
        }
    } catch (error) {
        console.error('Error deleting category:', error);
        showAlert('Error deleting category', 'danger');
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', async () => {
    await loadLanguages();
    loadCategories();
    
    document.getElementById('create-category-btn').addEventListener('click', createCategory);
    document.getElementById('save-category-btn').addEventListener('click', saveCategory);
    
    // Reload category options and render translation inputs when modals are shown
    document.getElementById('createCategoryModal').addEventListener('shown.bs.modal', () => {
        loadCategoryOptions();
        renderTranslationInputs('create-translations-container');
    });
    document.getElementById('editCategoryModal').addEventListener('shown.bs.modal', loadCategoryOptions);
});
