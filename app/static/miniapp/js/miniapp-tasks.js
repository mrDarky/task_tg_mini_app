// Tasks page functionality
let currentUser = null;
let allTasks = [];
let allCategories = [];
let currentFilter = 'all';

// Load categories from API
async function loadCategories() {
    try {
        const response = await window.miniApp.apiRequest('/categories');
        if (response && response.categories) {
            allCategories = response.categories;
            renderCategoryFilters();
        }
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

// Render category filter buttons
function renderCategoryFilters() {
    const container = document.getElementById('categoryFilters');
    const allButton = container.querySelector('[data-category="all"]');
    
    // Remove existing category buttons (keep "All" button)
    const existingButtons = container.querySelectorAll('button[data-category]:not([data-category="all"])');
    existingButtons.forEach(btn => btn.remove());
    
    // Add category buttons from database
    allCategories.forEach(category => {
        const button = document.createElement('button');
        button.className = 'btn btn-sm btn-outline-primary';
        button.setAttribute('data-category', category.id);
        button.textContent = category.name;
        button.addEventListener('click', () => {
            filterTasks(category.id);
        });
        container.appendChild(button);
    });
}

// Load user and tasks
async function loadData() {
    const tgUser = window.miniApp.getTelegramUser();
    currentUser = await window.miniApp.getUserByTelegramId(tgUser.id);
    
    if (currentUser) {
        document.getElementById('starBalance').textContent = window.miniApp.formatNumber(currentUser.stars);
        await loadCategories();
        await loadTasks();
    }
}

// Load all tasks
async function loadTasks() {
    const container = document.getElementById('tasksList');
    window.miniApp.showLoading(container);
    
    const response = await window.miniApp.apiRequest('/tasks?status=active');
    const tasks = response && response.tasks ? response.tasks : response;
    
    if (tasks && tasks.length > 0) {
        allTasks = tasks;
        filterTasks(currentFilter);
    } else {
        container.innerHTML = '<div class="empty-state"><i class="bi bi-inbox"></i><p>No tasks available</p></div>';
    }
}

// Filter tasks by category
function filterTasks(category) {
    currentFilter = category;
    const container = document.getElementById('tasksList');
    
    let filteredTasks = allTasks;
    if (category !== 'all') {
        // Filter by category_id
        filteredTasks = allTasks.filter(task => task.category_id === category);
    }
    
    if (filteredTasks.length > 0) {
        container.innerHTML = filteredTasks.map(task => window.miniApp.createTaskCard(task)).join('');
    } else {
        container.innerHTML = '<div class="empty-state"><i class="bi bi-inbox"></i><p>No tasks in this category</p></div>';
    }
    
    // Update filter buttons
    document.querySelectorAll('#categoryFilters button').forEach(btn => {
        btn.classList.remove('btn-primary', 'active');
        btn.classList.add('btn-outline-primary');
    });
    
    const activeBtn = document.querySelector(`#categoryFilters button[data-category="${category}"]`);
    if (activeBtn) {
        activeBtn.classList.remove('btn-outline-primary');
        activeBtn.classList.add('btn-primary', 'active');
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    loadData();
});
