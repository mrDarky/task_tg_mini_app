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
    
    try {
        // Completed tasks
        const completedTasks = await apiRequest(`/users/${currentUser.id}/tasks?status=completed`);
        const completedCount = completedTasks && Array.isArray(completedTasks) ? completedTasks.length : 0;
        document.getElementById('completedTasks').textContent = completedCount;
        
        // Referral count
        const referrals = await apiRequest(`/api/users/${currentUser.id}/referrals`);
        const referralCount = referrals && Array.isArray(referrals) ? referrals.length : 0;
        document.getElementById('referralCount').textContent = referralCount;
        
        // Achievements count will be set by loadAchievements()
        
        // Total earned (same as balance for now)
        document.getElementById('totalEarned').textContent = formatNumber(currentUser.stars);
    } catch (error) {
        console.error('Error loading statistics:', error);
        document.getElementById('completedTasks').textContent = '0';
        document.getElementById('referralCount').textContent = '0';
        document.getElementById('achievementCount').textContent = '0';
        document.getElementById('totalEarned').textContent = formatNumber(currentUser.stars || 0);
    }
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
    
    try {
        // Fetch achievements from API
        const achievements = await apiRequest(`/api/users/${currentUser.id}/achievements`);
        
        if (achievements && achievements.length > 0) {
            // Update achievement count
            const earnedCount = achievements.filter(ach => ach.earned).length;
            document.getElementById('achievementCount').textContent = earnedCount;
            
            // Display achievement badges
            container.innerHTML = achievements.map(ach => `
                <div class="achievement-badge ${ach.earned ? '' : 'locked'}" title="${ach.name}: ${ach.description}">
                    ${ach.icon}
                </div>
            `).join('');
        } else {
            // No achievements available
            container.innerHTML = '<p class="text-muted small">No achievements available yet.</p>';
        }
    } catch (error) {
        console.error('Error loading achievements:', error);
        // Fallback to showing placeholder
        container.innerHTML = '<p class="text-muted small">Unable to load achievements.</p>';
    }
}

// Setup referral section
async function setupReferralSection() {
    if (!currentUser) return;
    
    let referralCode = currentUser.referral_code;
    
    // If user doesn't have a referral code, generate one
    if (!referralCode) {
        try {
            const response = await apiRequest(`/api/users/${currentUser.id}/generate-referral`, {
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
    
    // Format the referral URL as: https://t.me/botname?start=CODE
    const botUsername = window.botUsername || 'TaskAppBot';
    const referralUrl = `https://t.me/${botUsername}?start=${referralCode}`;
    
    document.getElementById('referralCode').value = referralCode;
    
    // Also display the full link
    const referralLinkDisplay = document.getElementById('referralLinkDisplay');
    if (referralLinkDisplay) {
        referralLinkDisplay.textContent = referralUrl;
    }
    
    // Copy code button
    document.getElementById('copyCodeBtn').addEventListener('click', () => {
        copyToClipboard(referralCode);
    });
    
    // Share button
    document.getElementById('shareBtn').addEventListener('click', () => {
        const shareText = window.i18n?.t('invite_friends') || `Join Task App and earn stars by completing simple tasks! Use my referral code: ${referralCode}`;
        shareLink(referralUrl, shareText);
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    loadProfileData();
});
