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
    
    try {
        // Get completed tasks count
        const completedTasks = await apiRequest(`/users/${currentUser.id}/tasks?status=completed`);
        const completedCount = completedTasks && Array.isArray(completedTasks) ? completedTasks.length : 0;
        document.getElementById('completedTasks').textContent = completedCount;
        
        // Get referral count
        const referralsResponse = await apiRequest(`/users/${currentUser.id}/referrals`);
        const referralCount = referralsResponse && Array.isArray(referralsResponse) ? referralsResponse.length : 0;
        document.getElementById('referralCount').textContent = referralCount;
    } catch (error) {
        console.error('Error loading user stats:', error);
        document.getElementById('completedTasks').textContent = '0';
        document.getElementById('referralCount').textContent = '0';
    }
}

// Load quick tasks
async function loadQuickTasks() {
    const container = document.getElementById('quickTasks');
    showLoading(container);
    
    const response = await apiRequest('/tasks?status=active&limit=3&exclude_completed=true');
    const tasks = response && response.tasks ? response.tasks : (Array.isArray(response) ? response : []);
    
    if (tasks && tasks.length > 0) {
        container.innerHTML = tasks.map(task => window.miniApp.createTaskCard(task)).join('');
    } else {
        container.innerHTML = '<div class="empty-state"><i class="bi bi-inbox"></i><p>No tasks available</p></div>';
    }
}

// Check daily bonus status
async function checkDailyBonus() {
    if (!currentUser) return;
    
    try {
        // Get the last bonus claim for this user
        const bonusResponse = await apiRequest(`/users/${currentUser.id}/daily-bonus`);
        
        if (bonusResponse) {
            const lastClaimed = bonusResponse.last_claimed;
            const streakCount = bonusResponse.streak_count || 0;
            const canClaim = bonusResponse.can_claim || false;
            
            if (canClaim) {
                document.getElementById('bonusStatus').textContent = window.i18n?.t('claim_bonus') || 'Ready to claim!';
                document.getElementById('claimBonusBtn').disabled = false;
            } else {
                document.getElementById('bonusStatus').textContent = 'Already claimed today';
                document.getElementById('claimBonusBtn').disabled = true;
            }
            
            document.getElementById('streakText').textContent = `${window.i18n?.t('streak') || 'Streak'}: ${streakCount} ${window.i18n?.t('days') || 'days'}`;
            const progressPercent = Math.min((streakCount / 7) * 100, 100);
            document.getElementById('streakProgress').style.width = `${progressPercent}%`;
        } else {
            // First time user, bonus is available
            document.getElementById('bonusStatus').textContent = window.i18n?.t('claim_bonus') || 'Ready to claim!';
            document.getElementById('streakText').textContent = `${window.i18n?.t('streak') || 'Streak'}: 0 ${window.i18n?.t('days') || 'days'}`;
            document.getElementById('streakProgress').style.width = '0%';
        }
    } catch (error) {
        console.error('Error checking daily bonus:', error);
        // Default to showing as available
        document.getElementById('bonusStatus').textContent = window.i18n?.t('claim_bonus') || 'Ready to claim!';
        document.getElementById('streakText').textContent = `${window.i18n?.t('streak') || 'Streak'}: 0 ${window.i18n?.t('days') || 'days'}`;
        document.getElementById('streakProgress').style.width = '0%';
    }
}

// Claim daily bonus
async function claimDailyBonus() {
    if (!currentUser) return;
    
    const button = document.getElementById('claimBonusBtn');
    button.disabled = true;
    button.textContent = window.i18n?.t('claiming') || 'Claiming...';
    
    try {
        // Make API call to claim bonus
        const response = await apiRequest(`/users/${currentUser.id}/claim-bonus`, {
            method: 'POST'
        });
        
        if (response && response.success) {
            window.miniApp.showSuccess(window.i18n?.t('bonus_claimed') || `Daily bonus claimed! +${response.bonus_amount} ⭐`);
            
            // Update UI to reflect claimed status
            document.getElementById('bonusStatus').textContent = window.i18n?.t('already_claimed_today') || 'Already claimed today';
            document.getElementById('streakText').textContent = `${window.i18n?.t('streak') || 'Streak'}: ${response.streak_count} ${window.i18n?.t('days') || 'days'}`;
            const progressPercent = Math.min((response.streak_count / 7) * 100, 100);
            document.getElementById('streakProgress').style.width = `${progressPercent}%`;
            
            // Update star balance
            document.getElementById('starBalance').textContent = window.miniApp.formatNumber(response.total_stars);
            
            // Keep button disabled
            button.disabled = true;
            button.textContent = window.i18n?.t('claimed') || 'Claimed';
        } else {
            // Handle case where API returns success: false
            const errorMsg = response?.message || window.i18n?.t('failed_to_claim') || 'Failed to claim bonus';
            window.miniApp.showError(errorMsg);
            // Re-enable button on error
            button.disabled = false;
            button.textContent = window.i18n?.t('claim_btn') || 'Claim';
        }
    } catch (error) {
        window.miniApp.showError(error.message || window.i18n?.t('failed_to_claim') || 'Failed to claim bonus');
        // Re-enable button on error
        button.disabled = false;
        button.textContent = window.i18n?.t('claim_btn') || 'Claim';
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    loadUserData();
    
    const claimBtn = document.getElementById('claimBonusBtn');
    if (claimBtn) {
        claimBtn.addEventListener('click', claimDailyBonus);
    }
});
