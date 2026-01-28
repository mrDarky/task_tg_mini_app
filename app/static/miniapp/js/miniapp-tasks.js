// Tasks page functionality
const { getTelegramUser, getUserByTelegramId, apiRequest, showLoading, createTaskCard } = window.miniApp;

let currentUser = null;
let allTasks = [];
let currentFilter = 'all';

// Load user and tasks
async function loadData() {
    const tgUser = getTelegramUser();
    currentUser = await getUserByTelegramId(tgUser.id);
    
    if (currentUser) {
        document.getElementById('starBalance').textContent = window.miniApp.formatNumber(currentUser.stars);
        await loadTasks();
    }
}

// Load all tasks
async function loadTasks() {
    const container = document.getElementById('tasksList');
    showLoading(container);
    
    const tasks = await apiRequest('/tasks?status=active');
    
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
        filteredTasks = allTasks.filter(task => task.type === category);
    }
    
    if (filteredTasks.length > 0) {
        container.innerHTML = filteredTasks.map(task => createTaskCard(task)).join('');
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
    
    // Category filter buttons
    document.querySelectorAll('#categoryFilters button').forEach(button => {
        button.addEventListener('click', () => {
            const category = button.getAttribute('data-category');
            filterTasks(category);
        });
    });
});
