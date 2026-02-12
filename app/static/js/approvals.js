// Approvals page functionality
let currentPage = 0;
let currentLimit = 20;
let currentSubmissionId = null;

// Show notification (using Bootstrap's alert or a toast if available)
function showNotification(message, type = 'success') {
    // Try to use existing showAlert function from main.js
    if (typeof showAlert === 'function') {
        showAlert(message, type);
    } else {
        // Fallback to simple alert for now
        alert(message);
    }
}

// Load approvals on page load
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    loadApprovals();
});

// Load approval statistics
async function loadStats() {
    try {
        const response = await fetch('/api/approvals/stats/summary');
        if (response.ok) {
            const stats = await response.json();
            document.getElementById('statsPending').textContent = stats.pending || 0;
            document.getElementById('statsApprovedToday').textContent = stats.approved_today || 0;
            document.getElementById('statsRejectedToday').textContent = stats.rejected_today || 0;
            document.getElementById('statsTotalProcessed').textContent = stats.total_processed || 0;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load approvals list
async function loadApprovals(page = 0) {
    currentPage = page;
    const spinner = document.getElementById('loadingSpinner');
    const tbody = document.getElementById('approvalsTableBody');
    
    // Show spinner
    spinner.style.display = 'block';
    
    // Get filter values
    const status = document.getElementById('statusFilter').value;
    const taskType = document.getElementById('taskTypeFilter').value;
    const userId = document.getElementById('userIdFilter').value;
    
    // Build query string
    const params = new URLSearchParams({
        skip: page * currentLimit,
        limit: currentLimit
    });
    
    if (status) params.append('status', status);
    if (taskType) params.append('task_type', taskType);
    if (userId) params.append('user_id', userId);
    
    try {
        const response = await fetch(`/api/approvals?${params}`);
        if (!response.ok) {
            throw new Error('Failed to load approvals');
        }
        
        const data = await response.json();
        
        // Clear table
        tbody.innerHTML = '';
        
        // Populate table
        if (data.submissions && data.submissions.length > 0) {
            data.submissions.forEach(submission => {
                const row = createApprovalRow(submission);
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="8" class="text-center">No submissions found</td></tr>';
        }
        
        // Update pagination
        updatePagination(data.total, currentPage, currentLimit);
        
    } catch (error) {
        console.error('Error loading approvals:', error);
        tbody.innerHTML = '<tr><td colspan="8" class="text-center text-danger">Error loading approvals</td></tr>';
    } finally {
        spinner.style.display = 'none';
    }
}

// Create approval row
function createApprovalRow(submission) {
    const tr = document.createElement('tr');
    
    // Format date
    const submittedDate = new Date(submission.submitted_at).toLocaleString();
    
    // Status badge
    let statusBadge = '';
    switch(submission.status) {
        case 'pending':
            statusBadge = '<span class="badge bg-warning">Pending</span>';
            break;
        case 'approved':
            statusBadge = '<span class="badge bg-success">Approved</span>';
            break;
        case 'rejected':
            statusBadge = '<span class="badge bg-danger">Rejected</span>';
            break;
    }
    
    tr.innerHTML = `
        <td>${submission.id}</td>
        <td>
            <strong>${submission.username || 'N/A'}</strong><br>
            <small class="text-muted">ID: ${submission.user_id} | TG: ${submission.telegram_id}</small>
        </td>
        <td>
            <strong>${submission.task_title}</strong><br>
            <small class="text-muted">Task ID: ${submission.task_id}</small>
        </td>
        <td><span class="badge bg-info">${submission.task_type}</span></td>
        <td>${submission.task_reward} ⭐</td>
        <td>${statusBadge}</td>
        <td><small>${submittedDate}</small></td>
        <td>
            <button class="btn btn-sm btn-primary" onclick="viewSubmission(${submission.id})">
                <i class="bi bi-eye"></i> Review
            </button>
        </td>
    `;
    
    return tr;
}

// View submission details
async function viewSubmission(submissionId) {
    currentSubmissionId = submissionId;
    
    try {
        const response = await fetch(`/api/approvals/${submissionId}`);
        if (!response.ok) {
            throw new Error('Failed to load submission details');
        }
        
        const submission = await response.json();
        
        // Populate modal
        const modalBody = document.getElementById('approvalModalBody');
        const submittedDate = new Date(submission.submitted_at).toLocaleString();
        const reviewedDate = submission.reviewed_at ? new Date(submission.reviewed_at).toLocaleString() : 'N/A';
        
        modalBody.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>User Information</h6>
                    <table class="table table-sm">
                        <tr><th>Username:</th><td>${submission.username || 'N/A'}</td></tr>
                        <tr><th>User ID:</th><td>${submission.user_id}</td></tr>
                        <tr><th>Telegram ID:</th><td>${submission.telegram_id}</td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6>Task Information</h6>
                    <table class="table table-sm">
                        <tr><th>Task:</th><td>${submission.task_title}</td></tr>
                        <tr><th>Type:</th><td><span class="badge bg-info">${submission.task_type}</span></td></tr>
                        <tr><th>Reward:</th><td>${submission.task_reward} ⭐</td></tr>
                    </table>
                </div>
            </div>
            
            <hr>
            
            <div class="row">
                <div class="col-12">
                    <h6>Submission Details</h6>
                    <table class="table table-sm">
                        <tr><th>Status:</th><td><span class="badge bg-${submission.status === 'pending' ? 'warning' : submission.status === 'approved' ? 'success' : 'danger'}">${submission.status}</span></td></tr>
                        <tr><th>Submitted:</th><td>${submittedDate}</td></tr>
                        <tr><th>Reviewed:</th><td>${reviewedDate}</td></tr>
                        <tr><th>Submission Type:</th><td>${submission.submission_type}</td></tr>
                        ${submission.file_id ? `<tr><th>File ID:</th><td><code>${submission.file_id}</code></td></tr>` : ''}
                        ${submission.admin_notes ? `<tr><th>Admin Notes:</th><td>${submission.admin_notes}</td></tr>` : ''}
                    </table>
                </div>
            </div>
            
            ${submission.status === 'pending' ? `
            <hr>
            <div class="row">
                <div class="col-12">
                    <label for="adminNotes" class="form-label">Admin Notes (Optional)</label>
                    <textarea class="form-control" id="adminNotes" rows="3" placeholder="Add notes about this approval/rejection..."></textarea>
                </div>
            </div>
            ` : ''}
        `;
        
        // Show/hide action buttons based on status
        const approveBtn = document.getElementById('approveBtn');
        const rejectBtn = document.getElementById('rejectBtn');
        
        if (submission.status === 'pending') {
            approveBtn.style.display = 'block';
            rejectBtn.style.display = 'block';
        } else {
            approveBtn.style.display = 'none';
            rejectBtn.style.display = 'none';
        }
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('approvalModal'));
        modal.show();
        
    } catch (error) {
        console.error('Error loading submission details:', error);
        showNotification('Failed to load submission details', 'danger');
    }
}

// Process submission (approve/reject)
async function processSubmission(status) {
    if (!currentSubmissionId) return;
    
    const adminNotes = document.getElementById('adminNotes')?.value || '';
    
    const data = {
        status: status,
        admin_notes: adminNotes
    };
    
    try {
        const response = await fetch(`/api/approvals/${currentSubmissionId}/approve`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to process submission');
        }
        
        const result = await response.json();
        
        // Show success message
        showNotification(`Submission ${status} successfully!`, 'success');
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('approvalModal'));
        modal.hide();
        
        // Reload approvals and stats
        loadApprovals(currentPage);
        loadStats();
        
    } catch (error) {
        console.error('Error processing submission:', error);
        showNotification(`Failed to ${status} submission: ${error.message}`, 'danger');
    }
}

// Update pagination
function updatePagination(total, currentPage, limit) {
    const pagination = document.getElementById('pagination');
    const totalPages = Math.ceil(total / limit);
    
    pagination.innerHTML = '';
    
    if (totalPages <= 1) return;
    
    // Previous button
    const prevLi = document.createElement('li');
    prevLi.className = `page-item ${currentPage === 0 ? 'disabled' : ''}`;
    prevLi.innerHTML = `<a class="page-link" href="#" onclick="loadApprovals(${currentPage - 1}); return false;">Previous</a>`;
    pagination.appendChild(prevLi);
    
    // Page numbers
    const startPage = Math.max(0, currentPage - 2);
    const endPage = Math.min(totalPages - 1, currentPage + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        const li = document.createElement('li');
        li.className = `page-item ${i === currentPage ? 'active' : ''}`;
        li.innerHTML = `<a class="page-link" href="#" onclick="loadApprovals(${i}); return false;">${i + 1}</a>`;
        pagination.appendChild(li);
    }
    
    // Next button
    const nextLi = document.createElement('li');
    nextLi.className = `page-item ${currentPage >= totalPages - 1 ? 'disabled' : ''}`;
    nextLi.innerHTML = `<a class="page-link" href="#" onclick="loadApprovals(${currentPage + 1}); return false;">Next</a>`;
    pagination.appendChild(nextLi);
}
