// Tasks page functionality
let currentUser = null;
let allTasks = [];
let allCategories = [];
let currentFilter = 'all';
let showingHistory = false;

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
    
    const endpoint = showingHistory 
        ? `/users/${currentUser.id}/tasks?status=completed`
        : '/tasks?status=active&exclude_completed=true';
    
    const response = await window.miniApp.apiRequest(endpoint);
    
    // Handle different response formats
    let tasks;
    if (showingHistory) {
        // User tasks endpoint returns array directly
        tasks = Array.isArray(response) ? response : [];
    } else {
        // Tasks endpoint returns {tasks: [...], total: n, skip: n, limit: n}
        tasks = response && response.tasks ? response.tasks : [];
    }
    
    if (tasks && tasks.length > 0) {
        allTasks = tasks;
        filterTasks(currentFilter);
    } else {
        const emptyMessage = showingHistory 
            ? 'No completed tasks yet'
            : 'No tasks available';
        container.innerHTML = `<div class="empty-state"><i class="bi bi-inbox"></i><p>${emptyMessage}</p></div>`;
    }
}

// Filter tasks by category
function filterTasks(category) {
    currentFilter = category;
    const container = document.getElementById('tasksList');
    
    let filteredTasks = allTasks;
    if (category !== 'all') {
        // Filter by category_id - convert both to numbers for comparison
        const categoryId = typeof category === 'string' ? parseInt(category) : category;
        filteredTasks = allTasks.filter(task => task.category_id === categoryId);
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

// Toggle between new tasks and task history
function toggleTaskHistory() {
    showingHistory = !showingHistory;
    
    // Update header text and button
    const headerText = document.querySelector('.header h5');
    const historyBtn = document.getElementById('taskHistoryBtn');
    
    if (showingHistory) {
        headerText.textContent = '📜 Task History';
        historyBtn.innerHTML = '<i class="bi bi-arrow-left"></i>';
        historyBtn.title = 'Back to new tasks';
    } else {
        headerText.textContent = '📋 Available Tasks';
        historyBtn.innerHTML = '<i class="bi bi-clock-history"></i>';
        historyBtn.title = 'View task history';
    }
    
    // Reload tasks
    loadTasks();
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    loadData();
    
    // Task history button
    const historyBtn = document.getElementById('taskHistoryBtn');
    if (historyBtn) {
        historyBtn.addEventListener('click', toggleTaskHistory);
    }
});
