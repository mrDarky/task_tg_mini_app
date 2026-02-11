// Ticket detail page functionality
const { getTelegramUser, getUserByTelegramId, apiRequest, showError, showSuccess } = window.miniApp;

let currentUser = null;
let ticketId = null;
let currentTicket = null;

// Get ticket ID from URL
function getTicketIdFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('id');
}

// Load user data and ticket
async function loadUserData() {
    const tgUser = getTelegramUser();
    currentUser = await getUserByTelegramId(tgUser.id);
    
    ticketId = getTicketIdFromUrl();
    
    if (!ticketId) {
        showError('No ticket ID provided');
        setTimeout(() => {
            window.location.href = '/miniapp/support';
        }, 2000);
        return;
    }
    
    if (currentUser) {
        await loadTicket();
        await loadResponses();
    }
}

// Load ticket details
async function loadTicket() {
    const container = document.getElementById('ticketInfo');
    
    try {
        currentTicket = await apiRequest(`/tickets/${ticketId}`);
        
        if (!currentTicket) {
            container.innerHTML = `
                <div class="alert alert-danger mb-0">
                    <i class="bi bi-exclamation-triangle"></i>
                    Ticket not found
                </div>
            `;
            return;
        }
        
        // Check if user owns this ticket
        if (currentTicket.user_id !== currentUser.id) {
            container.innerHTML = `
                <div class="alert alert-danger mb-0">
                    <i class="bi bi-exclamation-triangle"></i>
                    You don't have permission to view this ticket
                </div>
            `;
            document.getElementById('responseFormCard').style.display = 'none';
            return;
        }
        
        const statusColors = {
            'open': 'primary',
            'in_progress': 'warning',
            'resolved': 'success',
            'closed': 'secondary'
        };
        
        const priorityColors = {
            'low': 'secondary',
            'medium': 'info',
            'high': 'warning',
            'urgent': 'danger'
        };
        
        const statusColor = statusColors[currentTicket.status] || 'secondary';
        const priorityColor = priorityColors[currentTicket.priority] || 'secondary';
        const date = new Date(currentTicket.created_at).toLocaleString();
        
        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-start mb-3">
                <div>
                    <span class="badge bg-${statusColor} me-2">${currentTicket.status.replace('_', ' ')}</span>
                    <span class="badge bg-${priorityColor}">${currentTicket.priority}</span>
                </div>
                <small class="text-muted">${date}</small>
            </div>
            <h5 class="mb-3">${currentTicket.subject}</h5>
            <div class="bg-light p-3 rounded">
                <p class="mb-0" style="white-space: pre-wrap;">${currentTicket.message}</p>
            </div>
        `;
        
        // Hide response form if ticket is closed
        if (currentTicket.status === 'closed' || currentTicket.status === 'resolved') {
            const responseFormCard = document.getElementById('responseFormCard');
            responseFormCard.innerHTML = `
                <div class="card-body">
                    <div class="alert alert-info mb-0">
                        <i class="bi bi-info-circle"></i>
                        This ticket is ${currentTicket.status}. You cannot add new responses.
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading ticket:', error);
        container.innerHTML = `
            <div class="alert alert-danger mb-0">
                <i class="bi bi-exclamation-triangle"></i>
                Failed to load ticket. Please try again.
            </div>
        `;
    }
}

// Load ticket responses
async function loadResponses() {
    const container = document.getElementById('ticketResponses');
    
    try {
        const responses = await apiRequest(`/tickets/${ticketId}/responses`);
        
        if (responses && responses.length > 0) {
            container.innerHTML = responses.map(response => createResponseCard(response)).join('');
        } else {
            container.innerHTML = `
                <div class="text-center text-muted py-3">
                    <i class="bi bi-chat-dots fs-3"></i>
                    <p class="mb-0">No responses yet</p>
                    <small>Responses from support team will appear here</small>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading responses:', error);
        container.innerHTML = `
            <div class="alert alert-warning mb-0">
                <i class="bi bi-exclamation-triangle"></i>
                Unable to load responses. Please try again later.
            </div>
        `;
    }
}

// Create response card HTML
function createResponseCard(response) {
    const date = new Date(response.created_at).toLocaleString();
    const isAdmin = response.is_admin;
    
    return `
        <div class="mb-3 ${isAdmin ? 'ms-3' : 'me-3'}">
            <div class="card border-0" style="background-color: ${isAdmin ? '#e3f2fd' : '#f8f9fa'};">
                <div class="card-body p-3">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <strong class="text-${isAdmin ? 'primary' : 'dark'}">
                            ${isAdmin ? '🛡️ Support Team' : '👤 You'}
                        </strong>
                        <small class="text-muted">${date}</small>
                    </div>
                    <p class="mb-0" style="white-space: pre-wrap;">${response.message}</p>
                </div>
            </div>
        </div>
    `;
}

// Handle response form submission
async function handleResponseSubmit(event) {
    event.preventDefault();
    
    if (!currentTicket) {
        showError('Ticket not loaded');
        return;
    }
    
    if (currentTicket.status === 'closed' || currentTicket.status === 'resolved') {
        showError('Cannot add responses to closed or resolved tickets');
        return;
    }
    
    const message = document.getElementById('responseMessage').value.trim();
    
    if (!message) {
        showError('Please enter a message');
        return;
    }
    
    const submitBtn = document.getElementById('submitResponseBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Sending...';
    
    try {
        const response = await apiRequest(`/tickets/${ticketId}/responses`, {
            method: 'POST',
            body: JSON.stringify({
                user_id: currentUser.id,
                message: message
            })
        });
        
        if (response) {
            showSuccess('Response sent successfully!');
            
            // Reset form
            document.getElementById('responseForm').reset();
            
            // Reload responses
            await loadResponses();
        }
    } catch (error) {
        showError('Failed to send response. Please try again.');
        console.error('Response submission error:', error);
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-send"></i> Send Response';
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Load user data and ticket
    loadUserData();
    
    // Form submission
    const form = document.getElementById('responseForm');
    if (form) {
        form.addEventListener('submit', handleResponseSubmit);
    }
});
