// Profile page functionality
const { getTelegramUser, getUserByTelegramId, apiRequest, showLoading, formatNumber, formatDate, copyToClipboard, shareLink } = window.miniApp;

let currentUser = null;

// Load user profile data
async function loadProfileData() {
    const tgUser = getTelegramUser();
    currentUser = await getUserByTelegramId(tgUser.id);
    
    if (currentUser) {
        // Update profile info
        document.getElementById('username').textContent = `@${currentUser.username || 'Anonymous'}`;
        document.getElementById('memberSince').textContent = `Member since: ${formatDate(currentUser.created_at)}`;
        document.getElementById('userStatus').textContent = currentUser.status || 'Active';
        document.getElementById('starBalance').textContent = formatNumber(currentUser.stars);
        
        // Load statistics
        await loadStatistics();
        await loadStarHistory();
        await loadAchievements();
        
        // Setup referral section
        setupReferralSection();
    }
}

// Load user statistics
async function loadStatistics() {
    if (!currentUser) return;
    
    // Completed tasks
    const completedTasks = await apiRequest(`/users/${currentUser.id}/tasks?status=completed`);
    document.getElementById('completedTasks').textContent = completedTasks ? completedTasks.length : 0;
    
    // Referral count (mock for now)
    document.getElementById('referralCount').textContent = '0';
    
    // Achievements count (mock for now)
    document.getElementById('achievementCount').textContent = '0';
    
    // Total earned (same as balance for now)
    document.getElementById('totalEarned').textContent = formatNumber(currentUser.stars);
}

// Load star history and draw simple chart
async function loadStarHistory() {
    // This would load actual transaction history
    // For now, show a simple placeholder
    const canvas = document.getElementById('historyCanvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.parentElement.offsetWidth;
    canvas.height = 150;
    
    // Draw simple line chart (mock data)
    ctx.strokeStyle = '#667eea';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    const points = [10, 25, 40, 35, 50, 70, currentUser.stars || 70];
    const stepX = canvas.width / (points.length - 1);
    const maxY = Math.max(...points);
    
    points.forEach((point, index) => {
        const x = index * stepX;
        const y = canvas.height - (point / maxY * canvas.height * 0.8) - 10;
        
        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    
    ctx.stroke();
}

// Load achievements
async function loadAchievements() {
    const container = document.getElementById('achievementBadges');
    
    // Mock achievements for now
    const achievements = [
        { id: 1, icon: '🌟', name: 'First Task', earned: true },
        { id: 2, icon: '🔥', name: '7 Day Streak', earned: false },
        { id: 3, icon: '👥', name: '5 Referrals', earned: false },
        { id: 4, icon: '💯', name: '100 Tasks', earned: false }
    ];
    
    container.innerHTML = achievements.map(ach => `
        <div class="achievement-badge ${ach.earned ? '' : 'locked'}" title="${ach.name}">
            ${ach.icon}
        </div>
    `).join('');
}

// Setup referral section
async function setupReferralSection() {
    if (!currentUser) return;
    
    let referralCode = currentUser.referral_code;
    
    // If user doesn't have a referral code, generate one
    if (!referralCode) {
        try {
            const response = await apiRequest(`/users/${currentUser.id}/generate-referral`, {
                method: 'POST'
            });
            if (response && response.referral_code) {
                referralCode = response.referral_code;
                currentUser.referral_code = referralCode;
            }
        } catch (error) {
            console.error('Failed to generate referral code:', error);
            return;
        }
    }
    
    const referralUrl = `https://t.me/${window.botUsername || 'TaskAppBot'}?start=${referralCode}`;
    
    document.getElementById('referralCode').value = referralCode;
    
    // Copy code button
    document.getElementById('copyCodeBtn').addEventListener('click', () => {
        copyToClipboard(referralCode);
    });
    
    // Share button
    document.getElementById('shareBtn').addEventListener('click', () => {
        shareLink(referralUrl, 'Join Task App and earn stars by completing simple tasks! Use my referral code: ' + referralCode);
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    loadProfileData();
});
