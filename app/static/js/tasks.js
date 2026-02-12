let currentPage = 0;
let currentSearch = '';
let currentType = '';
let currentStatus = '';
const limit = 20;
let availableLanguages = [];
let availableCategories = [];

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
        const response = await fetch('/api/categories/');
        const data = await response.json();
        availableCategories = data.categories || [];
        populateTaskTypeOptions();
        populateCategoryOptions();
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

function populateTaskTypeOptions() {
    const typeFilterSelect = document.getElementById('type-filter');
    const createTypeSelect = document.getElementById('create-type');
    const editTypeSelect = document.getElementById('edit-type');
    
    // Generate unique task types from categories
    const uniqueTypes = [...new Set(availableCategories.map(cat => cat.name))];
    
    // Update type filter dropdown
    if (typeFilterSelect) {
        const currentValue = typeFilterSelect.value;
        // Keep "All Types" option
        typeFilterSelect.innerHTML = '<option value="">All Types</option>';
        uniqueTypes.forEach(type => {
            const option = document.createElement('option');
            option.value = type;
            option.textContent = type;
            typeFilterSelect.appendChild(option);
        });
        if (currentValue) typeFilterSelect.value = currentValue;
    }
    
    // Update create task type dropdown
    if (createTypeSelect) {
        createTypeSelect.innerHTML = '';
        uniqueTypes.forEach(type => {
            const option = document.createElement('option');
            option.value = type;
            option.textContent = type;
            createTypeSelect.appendChild(option);
        });
    }
    
    // Update edit task type dropdown
    if (editTypeSelect) {
        editTypeSelect.innerHTML = '';
        uniqueTypes.forEach(type => {
            const option = document.createElement('option');
            option.value = type;
            option.textContent = type;
            editTypeSelect.appendChild(option);
        });
    }
}

function populateCategoryOptions() {
    const createCategorySelect = document.getElementById('create-category');
    const editCategorySelect = document.getElementById('edit-category');
    
    [createCategorySelect, editCategorySelect].forEach(select => {
        if (select) {
            const currentValue = select.value;
            select.innerHTML = '<option value="">None</option>';
            availableCategories.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat.id;
                option.textContent = cat.name;
                select.appendChild(option);
            });
            if (currentValue) select.value = currentValue;
        }
    });
}

async function loadTasks() {
    try {
        const params = new URLSearchParams({
            skip: currentPage * limit,
            limit: limit
        });
        
        if (currentSearch) params.append('search', currentSearch);
        if (currentType) params.append('task_type', currentType);
        if (currentStatus) params.append('status', currentStatus);
        
        const response = await fetch(`/api/tasks?${params}`);
        const data = await response.json();
        
        displayTasks(data.tasks);
        updatePagination(data.total);
    } catch (error) {
        console.error('Error loading tasks:', error);
        showAlert('Error loading tasks', 'danger');
    }
}

function displayTasks(tasks) {
    const tbody = document.getElementById('tasks-table-body');
    
    if (tasks.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center">No tasks found</td></tr>';
        return;
    }
    
    tbody.innerHTML = tasks.map(task => `
        <tr>
            <td><input type="checkbox" class="task-checkbox" value="${task.id}"></td>
            <td>${task.id}</td>
            <td>${task.title}</td>
            <td><span class="badge bg-info">${task.type}</span></td>
            <td><span class="badge bg-warning">${task.reward} ⭐</span></td>
            <td><span class="badge bg-${task.status === 'active' ? 'success' : 'secondary'}">${task.status}</span></td>
            <td>${task.category_id || 'N/A'}</td>
            <td>${formatDate(task.created_at)}</td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-primary" onclick="editTask(${task.id})">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-danger" onclick="deleteTask(${task.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
    
    updateBulkButtons();
}

function updatePagination(total) {
    const totalPages = Math.ceil(total / limit);
    const pagination = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    
    if (currentPage > 0) {
        html += `<li class="page-item"><a class="page-link" href="#" onclick="changePage(${currentPage - 1}); return false;">Previous</a></li>`;
    }
    
    for (let i = 0; i < totalPages; i++) {
        if (i === currentPage) {
            html += `<li class="page-item active"><a class="page-link" href="#">${i + 1}</a></li>`;
        } else if (Math.abs(i - currentPage) < 3 || i === 0 || i === totalPages - 1) {
            html += `<li class="page-item"><a class="page-link" href="#" onclick="changePage(${i}); return false;">${i + 1}</a></li>`;
        } else if (Math.abs(i - currentPage) === 3) {
            html += `<li class="page-item disabled"><a class="page-link" href="#">...</a></li>`;
        }
    }
    
    if (currentPage < totalPages - 1) {
        html += `<li class="page-item"><a class="page-link" href="#" onclick="changePage(${currentPage + 1}); return false;">Next</a></li>`;
    }
    
    pagination.innerHTML = html;
}

function changePage(page) {
    currentPage = page;
    loadTasks();
}

async function createTask() {
    const translations = getTranslationsFromInputs('create-translations-container');
    
    const categoryId = document.getElementById('create-category').value;
    const taskType = document.getElementById('create-type').value;
    
    const data = {
        title: document.getElementById('create-title').value,
        description: document.getElementById('create-description').value,
        type: taskType,
        url: document.getElementById('create-url').value,
        reward: parseInt(document.getElementById('create-reward').value),
        status: 'active',
        category_id: categoryId ? parseInt(categoryId) : null,
        translations: translations.length > 0 ? translations : undefined
    };
    
    // Add channel_id and verification_method for subscribe tasks
    if (taskType === 'subscribe') {
        const channelId = document.getElementById('create-channel-id').value;
        const verificationMethod = document.getElementById('create-verification-method').value;
        if (channelId) {
            data.channel_id = channelId;
        }
        data.verification_method = verificationMethod;
    }
    
    try {
        const response = await fetch('/api/tasks/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showAlert('Task created successfully', 'success');
            bootstrap.Modal.getInstance(document.getElementById('createTaskModal')).hide();
            document.getElementById('create-task-form').reset();
            loadTasks();
        } else {
            showAlert('Error creating task', 'danger');
        }
    } catch (error) {
        console.error('Error creating task:', error);
        showAlert('Error creating task', 'danger');
    }
}

async function editTask(taskId) {
    try {
        const response = await fetch(`/api/tasks/${taskId}?include_translations=true`);
        const task = await response.json();
        
        document.getElementById('edit-task-id').value = task.id;
        document.getElementById('edit-title').value = task.title;
        document.getElementById('edit-description').value = task.description || '';
        document.getElementById('edit-type').value = task.type;
        document.getElementById('edit-url').value = task.url || '';
        document.getElementById('edit-reward').value = task.reward;
        document.getElementById('edit-status').value = task.status;
        document.getElementById('edit-category').value = task.category_id || '';
        
        // Show/hide channel fields based on task type
        toggleChannelFields('edit', task.type);
        
        // Set channel fields if subscribe task
        if (task.type === 'subscribe') {
            document.getElementById('edit-channel-id').value = task.channel_id || '';
            document.getElementById('edit-verification-method').value = task.verification_method || 'manual';
        }
        
        // Render translation inputs with existing translations
        renderTranslationInputs('edit-translations-container', task.translations || []);
        
        const modal = new bootstrap.Modal(document.getElementById('editTaskModal'));
        modal.show();
    } catch (error) {
        console.error('Error loading task:', error);
        showAlert('Error loading task', 'danger');
    }
}

async function saveTask() {
    const taskId = document.getElementById('edit-task-id').value;
    const translations = getTranslationsFromInputs('edit-translations-container');
    
    const categoryId = document.getElementById('edit-category').value;
    const taskType = document.getElementById('edit-type').value;
    
    const data = {
        title: document.getElementById('edit-title').value,
        description: document.getElementById('edit-description').value,
        type: taskType,
        url: document.getElementById('edit-url').value,
        reward: parseInt(document.getElementById('edit-reward').value),
        status: document.getElementById('edit-status').value,
        category_id: categoryId ? parseInt(categoryId) : null,
        translations: translations.length > 0 ? translations : undefined
    };
    
    // Add channel_id and verification_method for subscribe tasks
    if (taskType === 'subscribe') {
        const channelId = document.getElementById('edit-channel-id').value;
        const verificationMethod = document.getElementById('edit-verification-method').value;
        if (channelId) {
            data.channel_id = channelId;
        }
        data.verification_method = verificationMethod;
    }
    
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showAlert('Task updated successfully', 'success');
            bootstrap.Modal.getInstance(document.getElementById('editTaskModal')).hide();
            loadTasks();
        } else {
            showAlert('Error updating task', 'danger');
        }
    } catch (error) {
        console.error('Error saving task:', error);
        showAlert('Error saving task', 'danger');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) return;
    
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showAlert('Task deleted successfully', 'success');
            loadTasks();
        } else {
            showAlert('Error deleting task', 'danger');
        }
    } catch (error) {
        console.error('Error deleting task:', error);
        showAlert('Error deleting task', 'danger');
    }
}

function getSelectedTaskIds() {
    const checkboxes = document.querySelectorAll('.task-checkbox:checked');
    return Array.from(checkboxes).map(cb => parseInt(cb.value));
}

function updateBulkButtons() {
    const selectedIds = getSelectedTaskIds();
    const hasSelection = selectedIds.length > 0;
    
    document.getElementById('bulk-deactivate-btn').disabled = !hasSelection;
    document.getElementById('bulk-activate-btn').disabled = !hasSelection;
}

async function bulkUpdateStatus(status) {
    const taskIds = getSelectedTaskIds();
    if (taskIds.length === 0) return;
    
    try {
        const response = await fetch('/api/tasks/bulk-update', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                task_ids: taskIds,
                update_data: {status: status}
            })
        });
        
        if (response.ok) {
            showAlert(`${taskIds.length} tasks updated`, 'success');
            loadTasks();
        } else {
            showAlert('Error in bulk operation', 'danger');
        }
    } catch (error) {
        console.error('Error in bulk update:', error);
        showAlert('Error in bulk operation', 'danger');
    }
}

// Toggle channel-specific fields based on task type
function toggleChannelFields(prefix, taskType) {
    const channelSection = document.getElementById(`${prefix}-channel-section`);
    const verificationSection = document.getElementById(`${prefix}-verification-section`);
    
    if (taskType === 'subscribe') {
        channelSection.style.display = 'block';
        verificationSection.style.display = 'block';
    } else {
        channelSection.style.display = 'none';
        verificationSection.style.display = 'none';
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', async () => {
    // Load languages and categories first
    await loadLanguages();
    await loadCategories();
    
    // Then load tasks
    loadTasks();
    
    // Add event listeners for task type change
    document.getElementById('create-type').addEventListener('change', (e) => {
        toggleChannelFields('create', e.target.value);
    });
    
    document.getElementById('edit-type').addEventListener('change', (e) => {
        toggleChannelFields('edit', e.target.value);
    });
    
    document.getElementById('search-btn').addEventListener('click', () => {
        currentSearch = document.getElementById('search-input').value;
        currentType = document.getElementById('type-filter').value;
        currentStatus = document.getElementById('status-filter').value;
        currentPage = 0;
        loadTasks();
    });
    
    document.getElementById('search-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            document.getElementById('search-btn').click();
        }
    });
    
    document.getElementById('select-all').addEventListener('change', (e) => {
        document.querySelectorAll('.task-checkbox').forEach(cb => {
            cb.checked = e.target.checked;
        });
        updateBulkButtons();
    });
    
    document.getElementById('tasks-table-body').addEventListener('change', (e) => {
        if (e.target.classList.contains('task-checkbox')) {
            updateBulkButtons();
        }
    });
    
    document.getElementById('create-task-btn').addEventListener('click', createTask);
    document.getElementById('save-task-btn').addEventListener('click', saveTask);
    document.getElementById('bulk-deactivate-btn').addEventListener('click', () => bulkUpdateStatus('inactive'));
    document.getElementById('bulk-activate-btn').addEventListener('click', () => bulkUpdateStatus('active'));
    
    // Render translation inputs when modals are shown
    document.getElementById('createTaskModal').addEventListener('shown.bs.modal', () => {
        renderTranslationInputs('create-translations-container');
    });
});

function renderTranslationInputs(containerId, translations = []) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = availableLanguages.map(lang => {
        const existingTrans = translations.find(t => t.language_id === lang.id);
        return `
            <div class="row mb-2">
                <div class="col-md-12">
                    <label class="form-label fw-bold">${lang.name} (${lang.code.toUpperCase()})</label>
                </div>
                <div class="col-md-12 mb-2">
                    <input type="text" 
                           class="form-control translation-title" 
                           data-language-id="${lang.id}"
                           value="${existingTrans ? existingTrans.title : ''}"
                           placeholder="Title in ${lang.name}">
                </div>
                <div class="col-md-12">
                    <textarea class="form-control translation-description" 
                              data-language-id="${lang.id}"
                              rows="2"
                              placeholder="Description in ${lang.name}">${existingTrans ? (existingTrans.description || '') : ''}</textarea>
                </div>
            </div>
        `;
    }).join('');
}

function getTranslationsFromInputs(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return [];
    
    const translations = [];
    
    availableLanguages.forEach(lang => {
        const titleInput = container.querySelector(`.translation-title[data-language-id="${lang.id}"]`);
        const descInput = container.querySelector(`.translation-description[data-language-id="${lang.id}"]`);
        
        if (titleInput && titleInput.value.trim()) {
            translations.push({
                language_id: lang.id,
                title: titleInput.value.trim(),
                description: descInput ? descInput.value.trim() : null
            });
        }
    });
    
    return translations;
}

