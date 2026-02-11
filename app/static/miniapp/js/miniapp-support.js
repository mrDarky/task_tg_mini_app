// Support page functionality
const { getTelegramUser, getUserByTelegramId, apiRequest, showError, showSuccess } = window.miniApp;

let currentUser = null;
let confirmModal = null;
let pendingTicketData = null;

// Load user data and tickets
async function loadUserData() {
    const tgUser = getTelegramUser();
    currentUser = await getUserByTelegramId(tgUser.id);
    
    if (currentUser) {
        await loadUserTickets();
    }
}

// Load user's tickets
async function loadUserTickets() {
    if (!currentUser) return;
    
    const container = document.getElementById('userTickets');
    
    try {
        // Fetch user's tickets
        const tickets = await apiRequest(`/tickets?user_id=${currentUser.id}`);
        
        if (tickets && tickets.length > 0) {
            container.innerHTML = tickets.slice(0, 5).map(ticket => createTicketCard(ticket)).join('');
        } else {
            container.innerHTML = `
                <div class="text-center text-muted py-3">
                    <i class="bi bi-inbox fs-3"></i>
                    <p class="mb-0">No tickets yet</p>
                    <small>Create a ticket to get help from our support team</small>
                </div>
            `;
        }
    } catch (error) {
        container.innerHTML = `
            <div class="alert alert-warning mb-0">
                <i class="bi bi-exclamation-triangle"></i>
                Unable to load tickets. Please try again later.
            </div>
        `;
    }
}

// Create ticket card HTML
function createTicketCard(ticket) {
    const statusColors = {
        'open': 'primary',
        'in_progress': 'warning',
        'resolved': 'success',
        'closed': 'secondary'
    };
    
    const statusColor = statusColors[ticket.status] || 'secondary';
    const date = new Date(ticket.created_at).toLocaleDateString();
    
    return `
        <div class="card mb-2 border-0 ticket-card" style="background-color: #f8f9fa; cursor: pointer;" onclick="openTicket(${ticket.id})">
            <div class="card-body p-2">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="mb-1">${ticket.subject}</h6>
                        <small class="text-muted">${date}</small>
                    </div>
                    <span class="badge bg-${statusColor}">${ticket.status.replace('_', ' ')}</span>
                </div>
                <p class="mb-1 mt-2 small text-muted">${ticket.message.substring(0, 80)}${ticket.message.length > 80 ? '...' : ''}</p>
            </div>
        </div>
    `;
}

// Open ticket detail page
function openTicket(ticketId) {
    window.location.href = `/miniapp/ticket-detail?id=${ticketId}`;
}

// Handle form submission
function handleFormSubmit(event) {
    event.preventDefault();
    
    const subject = document.getElementById('ticketSubject').value.trim();
    const message = document.getElementById('ticketMessage').value.trim();
    const priority = document.getElementById('ticketPriority').value;
    
    if (!subject || !message) {
        showError('Please fill in all required fields');
        return;
    }
    
    // Store ticket data for confirmation
    pendingTicketData = {
        user_id: currentUser.id,
        subject: subject,
        message: message,
        priority: priority
    };
    
    // Show confirmation modal
    confirmModal.show();
}

// Handle cancel button
function handleCancel() {
    const form = document.getElementById('ticketForm');
    form.reset();
    showSuccess('Form cleared');
}

// Handle confirm submission
async function handleConfirmSubmit() {
    if (!pendingTicketData) {
        showError('No ticket data to submit');
        return;
    }
    
    const submitBtn = document.getElementById('confirmSubmitBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Submitting...';
    
    try {
        const response = await apiRequest('/tickets', {
            method: 'POST',
            body: JSON.stringify(pendingTicketData)
        });
        
        if (response) {
            showSuccess('Ticket submitted successfully! Our team will respond soon.');
            
            // Reset form
            document.getElementById('ticketForm').reset();
            
            // Hide modal
            confirmModal.hide();
            
            // Reload tickets
            await loadUserTickets();
            
            // Clear pending data
            pendingTicketData = null;
        }
    } catch (error) {
        showError('Failed to submit ticket. Please try again.');
        console.error('Ticket submission error:', error);
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-check"></i> Confirm';
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Initialize modal
    confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));
    
    // Load user data
    loadUserData();
    
    // Form submission
    const form = document.getElementById('ticketForm');
    form.addEventListener('submit', handleFormSubmit);
    
    // Cancel button
    const cancelBtn = document.getElementById('cancelBtn');
    cancelBtn.addEventListener('click', handleCancel);
    
    // Confirm submit button
    const confirmSubmitBtn = document.getElementById('confirmSubmitBtn');
    confirmSubmitBtn.addEventListener('click', handleConfirmSubmit);
});
