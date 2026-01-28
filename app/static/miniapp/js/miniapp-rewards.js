// Rewards page functionality
const { getTelegramUser, getUserByTelegramId, apiRequest, showLoading, formatNumber, showSuccess, showError } = window.miniApp;

let currentUser = null;

// Load user data and rewards
async function loadData() {
    const tgUser = getTelegramUser();
    currentUser = await getUserByTelegramId(tgUser.id);
    
    if (currentUser) {
        document.getElementById('starBalance').textContent = formatNumber(currentUser.stars);
        await loadRewardCatalog();
        await loadTransactionHistory();
        await loadPartnerOffers();
    }
}

// Load reward catalog
async function loadRewardCatalog() {
    const container = document.getElementById('rewardCatalog');
    showLoading(container);
    
    // Mock reward items
    const rewards = [
        {
            id: 1,
            name: 'Amazon Gift Card $10',
            cost: 1000,
            image: 'https://via.placeholder.com/200x150?text=Amazon',
            available: true
        },
        {
            id: 2,
            name: 'PayPal Cash $5',
            cost: 500,
            image: 'https://via.placeholder.com/200x150?text=PayPal',
            available: true
        },
        {
            id: 3,
            name: 'Steam Gift Card $10',
            cost: 1000,
            image: 'https://via.placeholder.com/200x150?text=Steam',
            available: true
        },
        {
            id: 4,
            name: 'Netflix 1 Month',
            cost: 1500,
            image: 'https://via.placeholder.com/200x150?text=Netflix',
            available: true
        },
        {
            id: 5,
            name: 'Spotify Premium',
            cost: 800,
            image: 'https://via.placeholder.com/200x150?text=Spotify',
            available: true
        },
        {
            id: 6,
            name: 'Discord Nitro',
            cost: 900,
            image: 'https://via.placeholder.com/200x150?text=Discord',
            available: true
        }
    ];
    
    container.innerHTML = rewards.map(reward => `
        <div class="col-6 col-md-4">
            <div class="card reward-item border-0 shadow-sm">
                <img src="${reward.image}" alt="${reward.name}">
                <span class="reward-cost">⭐ ${reward.cost}</span>
                <div class="card-body">
                    <h6 class="mb-2">${reward.name}</h6>
                    <button class="btn btn-primary btn-sm w-100" 
                            onclick="redeemReward(${reward.id}, ${reward.cost})"
                            ${currentUser.stars < reward.cost ? 'disabled' : ''}>
                        ${currentUser.stars >= reward.cost ? 'Redeem' : 'Not Enough'}
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Redeem reward
window.redeemReward = function(rewardId, cost) {
    if (!currentUser || currentUser.stars < cost) {
        showError('Not enough stars!');
        return;
    }
    
    if (confirm(`Redeem this reward for ${cost} stars?`)) {
        // In a real app, this would make an API call
        showSuccess('Reward redemption request submitted!');
    }
};

// Submit withdrawal request
async function submitWithdrawal() {
    const amount = parseInt(document.getElementById('withdrawalAmount').value);
    const method = document.getElementById('withdrawalMethod').value;
    const details = document.getElementById('withdrawalDetails').value;
    
    if (!amount || amount < 100) {
        showError('Minimum withdrawal amount is 100 stars');
        return;
    }
    
    if (!method) {
        showError('Please select a withdrawal method');
        return;
    }
    
    if (!details) {
        showError('Please provide payment details');
        return;
    }
    
    if (currentUser.stars < amount) {
        showError('Insufficient balance');
        return;
    }
    
    try {
        const response = await apiRequest('/withdrawals', {
            method: 'POST',
            body: JSON.stringify({
                user_id: currentUser.id,
                amount: amount,
                method: method,
                details: details
            })
        });
        
        if (response) {
            showSuccess('Withdrawal request submitted successfully!');
            // Clear form
            document.getElementById('withdrawalAmount').value = '';
            document.getElementById('withdrawalMethod').value = '';
            document.getElementById('withdrawalDetails').value = '';
            // Reload data
            await loadData();
        }
    } catch (error) {
        showError('Failed to submit withdrawal request');
    }
}

// Load transaction history
async function loadTransactionHistory() {
    const container = document.getElementById('transactionHistory');
    showLoading(container);
    
    // Mock transaction data
    const transactions = [
        { id: 1, type: 'earned', amount: 50, description: 'Task completed', date: new Date() },
        { id: 2, type: 'bonus', amount: 10, description: 'Daily bonus', date: new Date(Date.now() - 86400000) },
        { id: 3, type: 'earned', amount: 30, description: 'Task completed', date: new Date(Date.now() - 172800000) }
    ];
    
    if (transactions.length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="bi bi-inbox"></i><p>No transactions yet</p></div>';
        return;
    }
    
    container.innerHTML = transactions.map(tx => `
        <div class="transaction-item">
            <div>
                <strong>${tx.description}</strong>
                <br>
                <small class="text-muted">${window.miniApp.formatDate(tx.date)}</small>
            </div>
            <div class="amount ${tx.amount > 0 ? 'positive' : 'negative'}">
                ${tx.amount > 0 ? '+' : ''}${tx.amount} ⭐
            </div>
        </div>
    `).join('');
}

// Load partner offers
async function loadPartnerOffers() {
    const container = document.getElementById('partnerOffers');
    
    // Mock partner offers
    const offers = [
        { id: 1, title: 'Special Offer: Double Stars', description: 'Complete tasks this week for 2x rewards!' },
        { id: 2, title: 'New: Bitcoin Withdrawal', description: 'Withdraw your stars as Bitcoin!' }
    ];
    
    if (offers.length === 0) {
        container.innerHTML = '<p class="text-muted">No offers available</p>';
        return;
    }
    
    container.innerHTML = offers.map(offer => `
        <div class="card border-0 shadow-sm">
            <div class="card-body">
                <h6 class="mb-1">${offer.title}</h6>
                <p class="text-muted small mb-0">${offer.description}</p>
            </div>
        </div>
    `).join('');
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    loadData();
    
    const submitBtn = document.getElementById('submitWithdrawal');
    if (submitBtn) {
        submitBtn.addEventListener('click', submitWithdrawal);
    }
});
