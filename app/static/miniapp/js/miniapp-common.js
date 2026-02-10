// Telegram Web App initialization
const tg = window.Telegram?.WebApp;
if (tg) {
    tg.ready();
    tg.expand();
}

// API Base URL
const API_BASE = '/api';

// Bot info (will be loaded on initialization)
window.botUsername = 'TaskAppBot'; // Default value

// Load bot info
const loadBotInfo = async function() {
    try {
        const response = await fetch('/api/settings/public/bot-info');
        if (response.ok) {
            const data = await response.json();
            window.botUsername = data.bot_username || 'TaskAppBot';
        }
    } catch (error) {
        console.warn('Failed to load bot info:', error);
    }
};

// Initialize bot info
loadBotInfo();

// Get Telegram user data
const getTelegramUser = function() {
    if (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) {
        return tg.initDataUnsafe.user;
    }
    // Fallback for testing
    return {
        id: 123456789,
        first_name: 'Test',
        username: 'testuser'
    };
};

// Fetch with error handling
const apiRequest = async function(endpoint, options = {}) {
    try {
        const response = await fetch(API_BASE + endpoint, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        showError('Failed to load data. Please try again.');
        return null;
    }
};

// Get user by Telegram ID
const getUserByTelegramId = async function(telegramId) {
    const response = await apiRequest(`/users?search=${telegramId}`);
    if (response && response.users && response.users.length > 0) {
        return response.users[0];
    }
    return null;
};

// Show toast notification
const showToast = function(message, type = 'success') {
    // Use Telegram's alert if available
    if (tg && tg.showAlert) {
        tg.showAlert(message);
        return;
    }
    
    // Fallback to custom toast
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed top-0 start-50 translate-middle-x mt-3`;
    toast.style.zIndex = '9999';
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
};

// Show error message
const showError = function(message) {
    showToast(message, 'danger');
};

// Show success message
const showSuccess = function(message) {
    showToast(message, 'success');
};

// Show loading spinner
const showLoading = function(element) {
    if (element) {
        element.innerHTML = '<div class="spinner"></div>';
    }
};

// Format date
const formatDate = function(dateString) {
    const date = new Date(dateString);
    const lang = window.i18n?.getCurrentLanguage() || 'en';
    const locales = {
        'en': 'en-US',
        'ru': 'ru-RU',
        'es': 'es-ES'
    };
    return date.toLocaleDateString(locales[lang] || 'en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
};

// Format number with commas
const formatNumber = function(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
};

// Get task type emoji
const getTaskTypeEmoji = function(type) {
    const emojis = {
        'youtube': '🎥',
        'tiktok': '🎵',
        'subscribe': '📢'
    };
    return emojis[type] || '📋';
};

// Get task type color
const getTaskTypeColor = function(type) {
    const colors = {
        'youtube': 'danger',
        'tiktok': 'dark',
        'subscribe': 'primary'
    };
    return colors[type] || 'secondary';
};

// Create task card HTML
const createTaskCard = function(task) {
    const emoji = getTaskTypeEmoji(task.type);
    const color = getTaskTypeColor(task.type);
    
    return `
        <div class="card task-card ${task.type} border-0 shadow-sm fade-in">
            <div class="card-body">
                <div class="d-flex align-items-start">
                    <div class="task-icon me-3">
                        ${emoji}
                    </div>
                    <div class="flex-grow-1">
                        <h6 class="mb-1">${task.title}</h6>
                        <p class="text-muted small mb-2">${task.description || 'Complete this task to earn stars'}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="badge bg-${color}">${task.type}</span>
                            <div class="d-flex align-items-center">
                                <i class="bi bi-star-fill text-warning me-1"></i>
                                <strong>${task.reward}</strong>
                            </div>
                        </div>
                    </div>
                </div>
                <button class="btn btn-primary btn-sm w-100 mt-3" onclick="window.miniApp.openTaskDetail(${task.id})">
                    View Details
                </button>
            </div>
        </div>
    `;
};

// Open task detail page
const openTaskDetail = function(taskId) {
    window.location.href = `/miniapp/task/${taskId}`;
};

// Initialize Telegram Web App theme
const initTheme = function() {
    if (tg && tg.colorScheme) {
        document.body.setAttribute('data-theme', tg.colorScheme);
    }
};

// Copy to clipboard
const copyToClipboard = function(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showSuccess(window.i18n?.t('copied_to_clipboard') || 'Copied to clipboard!');
        }).catch(() => {
            showError(window.i18n?.t('failed_to_copy') || 'Failed to copy');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showSuccess(window.i18n?.t('copied_to_clipboard') || 'Copied to clipboard!');
        } catch (err) {
            showError(window.i18n?.t('failed_to_copy') || 'Failed to copy');
        }
        document.body.removeChild(textArea);
    }
};

// Share link
const shareLink = function(url, text) {
    if (tg && tg.openTelegramLink) {
        tg.openTelegramLink(`https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`);
    } else if (navigator.share) {
        navigator.share({
            title: 'Task App',
            text: text,
            url: url
        }).catch(() => {
            showError('Failed to share');
        });
    } else {
        copyToClipboard(url);
    }
};

// Open external link
const openExternalLink = function(url) {
    if (tg && tg.openLink) {
        tg.openLink(url);
    } else {
        window.open(url, '_blank');
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
});

// Handle Telegram back button
if (tg && tg.BackButton) {
    tg.BackButton.onClick(() => {
        window.history.back();
    });
}

// Export functions for use in other scripts
window.miniApp = {
    getTelegramUser,
    getUserByTelegramId,
    apiRequest,
    showToast,
    showError,
    showSuccess,
    showLoading,
    formatDate,
    formatNumber,
    getTaskTypeEmoji,
    getTaskTypeColor,
    createTaskCard,
    openTaskDetail,
    copyToClipboard,
    shareLink,
    openExternalLink
};
