// Home page functionality
const { getTelegramUser, getUserByTelegramId, apiRequest, showLoading, formatNumber } = window.miniApp;

let currentUser = null;

// Load user data
async function loadUserData() {
    const tgUser = getTelegramUser();
    currentUser = await getUserByTelegramId(tgUser.id);
    
    if (currentUser) {
        document.getElementById('starBalance').textContent = formatNumber(currentUser.stars);
        await loadUserStats();
        await loadQuickTasks();
        await checkDailyBonus();
    }
}

// Load user statistics
async function loadUserStats() {
    if (!currentUser) return;
    
    // Get completed tasks count
    const completedTasks = await apiRequest(`/users/${currentUser.id}/tasks?status=completed`);
    document.getElementById('completedTasks').textContent = completedTasks ? completedTasks.length : 0;
    
    // Get referral count (mock data for now)
    document.getElementById('referralCount').textContent = '0';
}

// Load quick tasks
async function loadQuickTasks() {
    const container = document.getElementById('quickTasks');
    showLoading(container);
    
    const tasks = await apiRequest('/tasks?status=active&limit=5');
    
    if (tasks && tasks.length > 0) {
        container.innerHTML = tasks.map(task => window.miniApp.createTaskCard(task)).join('');
    } else {
        container.innerHTML = '<div class="empty-state"><i class="bi bi-inbox"></i><p>No tasks available</p></div>';
    }
}

// Check daily bonus status
async function checkDailyBonus() {
    // This would check the last bonus claim time
    // For now, show as available
    document.getElementById('bonusStatus').textContent = 'Ready to claim!';
    document.getElementById('streakText').textContent = 'Streak: 1 day';
    document.getElementById('streakProgress').style.width = '14%'; // 1/7 days
}

// Claim daily bonus
async function claimDailyBonus() {
    if (!currentUser) return;
    
    const button = document.getElementById('claimBonusBtn');
    button.disabled = true;
    button.textContent = 'Claiming...';
    
    try {
        // Make API call to claim bonus
        const response = await apiRequest(`/users/${currentUser.id}/claim-bonus`, {
            method: 'POST'
        });
        
        if (response) {
            window.miniApp.showSuccess('Daily bonus claimed! +10 ⭐');
            await loadUserData();
        }
    } catch (error) {
        window.miniApp.showError('Failed to claim bonus');
    } finally {
        button.disabled = false;
        button.textContent = 'Claim';
    }
}

// Handle notification button
function showNotifications() {
    window.miniApp.showToast('No new notifications');
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    loadUserData();
    
    const claimBtn = document.getElementById('claimBonusBtn');
    if (claimBtn) {
        claimBtn.addEventListener('click', claimDailyBonus);
    }
    
    const notifBtn = document.getElementById('notificationBtn');
    if (notifBtn) {
        notifBtn.addEventListener('click', showNotifications);
    }
});
