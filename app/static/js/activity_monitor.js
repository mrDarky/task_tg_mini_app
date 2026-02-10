// Activity Monitor JavaScript

let currentActivityPage = 0;
let currentIpPage = 0;
let currentSuspiciousPage = 0;
let currentBlockIpAddress = null;

// Load activities on page load
document.addEventListener('DOMContentLoaded', function() {
    loadActivities();
    loadIpAddresses();
    loadSuspiciousActivities();
    
    // Set up tab change listeners
    document.getElementById('activities-tab').addEventListener('shown.bs.tab', loadActivities);
    document.getElementById('ip-addresses-tab').addEventListener('shown.bs.tab', loadIpAddresses);
    document.getElementById('suspicious-tab').addEventListener('shown.bs.tab', loadSuspiciousActivities);
    
    // Set up enter key for search fields
    document.getElementById('activitySearch')?.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') loadActivities();
    });
    document.getElementById('ipSearch')?.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') loadIpAddresses();
    });
});

// Load activity logs
async function loadActivities(page = 0) {
    currentActivityPage = page;
    const tbody = document.getElementById('activityTableBody');
    tbody.innerHTML = '<tr><td colspan="8" class="text-center"><div class="spinner-border" role="status"></div></td></tr>';
    
    // Get filter values
    const search = document.getElementById('activitySearch').value;
    const userId = document.getElementById('activityUserId').value;
    const statusCode = document.getElementById('activityStatusCode').value;
    const startDate = document.getElementById('activityStartDate').value;
    const endDate = document.getElementById('activityEndDate').value;
    
    // Build query parameters
    const params = new URLSearchParams({
        offset: page * 50,
        limit: 50
    });
    
    if (search) params.append('search', search);
    if (userId) params.append('user_id', userId);
    if (statusCode) params.append('status_code', statusCode);
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    try {
        const response = await fetch(`/api/activity/logs?${params.toString()}`);
        const data = await response.json();
        
        displayActivities(data.activities);
        displayActivityPagination(data.total, page);
        document.getElementById('activityTotalCount').textContent = data.total;
    } catch (error) {
        console.error('Error loading activities:', error);
        tbody.innerHTML = '<tr><td colspan="8" class="text-center text-danger">Error loading activities</td></tr>';
    }
}

// Display activities in table
function displayActivities(activities) {
    const tbody = document.getElementById('activityTableBody');
    
    if (activities.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No activities found</td></tr>';
        return;
    }
    
    tbody.innerHTML = activities.map(activity => {
        const statusBadge = getStatusBadge(activity.status_code);
        const suspiciousBadge = activity.is_suspicious ? '<span class="badge bg-danger ms-2">Suspicious</span>' : '';
        const userDisplay = activity.username ? 
            `<a href="/admin/users?search=${activity.telegram_id}">${activity.username}</a>` : 
            '<span class="text-muted">Guest</span>';
        
        return `
            <tr class="${activity.is_suspicious ? 'table-warning' : ''}">
                <td><small>${formatDateTime(activity.created_at)}</small></td>
                <td>${userDisplay}</td>
                <td>
                    <a href="#" onclick="viewIpActivities('${activity.ip_address}'); return false;">
                        ${activity.ip_address}
                    </a>
                </td>
                <td><span class="badge bg-secondary">${activity.method}</span></td>
                <td><small>${activity.endpoint}</small></td>
                <td>${statusBadge}${suspiciousBadge}</td>
                <td><small>${activity.action_type || '-'}</small></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="viewActivityDetails(${activity.id})">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="showBlockIpModal('${activity.ip_address}')">
                        <i class="bi bi-ban"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// Display activity pagination
function displayActivityPagination(total, currentPage) {
    const pagination = document.getElementById('activityPagination');
    const totalPages = Math.ceil(total / 50);
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    
    // Previous button
    html += `
        <li class="page-item ${currentPage === 0 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="loadActivities(${currentPage - 1}); return false;">Previous</a>
        </li>
    `;
    
    // Page numbers
    for (let i = 0; i < Math.min(totalPages, 10); i++) {
        html += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="loadActivities(${i}); return false;">${i + 1}</a>
            </li>
        `;
    }
    
    // Next button
    html += `
        <li class="page-item ${currentPage >= totalPages - 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="loadActivities(${currentPage + 1}); return false;">Next</a>
        </li>
    `;
    
    pagination.innerHTML = html;
}

// Load IP addresses
async function loadIpAddresses(page = 0) {
    currentIpPage = page;
    const tbody = document.getElementById('ipTableBody');
    tbody.innerHTML = '<tr><td colspan="8" class="text-center"><div class="spinner-border" role="status"></div></td></tr>';
    
    // Get filter values
    const search = document.getElementById('ipSearch').value;
    const isBlocked = document.getElementById('ipBlockedFilter').value;
    const minSuspicious = document.getElementById('ipMinSuspicious').value;
    
    // Build query parameters
    const params = new URLSearchParams({
        offset: page * 50,
        limit: 50
    });
    
    if (search) params.append('search', search);
    if (isBlocked !== '') params.append('is_blocked', isBlocked);
    if (minSuspicious) params.append('min_suspicious_count', minSuspicious);
    
    try {
        const response = await fetch(`/api/activity/ip-addresses?${params.toString()}`);
        const data = await response.json();
        
        displayIpAddresses(data.ip_addresses);
        displayIpPagination(data.total, page);
        document.getElementById('ipTotalCount').textContent = data.total;
    } catch (error) {
        console.error('Error loading IP addresses:', error);
        tbody.innerHTML = '<tr><td colspan="8" class="text-center text-danger">Error loading IP addresses</td></tr>';
    }
}

// Display IP addresses in table
function displayIpAddresses(ipAddresses) {
    const tbody = document.getElementById('ipTableBody');
    
    if (ipAddresses.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No IP addresses found</td></tr>';
        return;
    }
    
    tbody.innerHTML = ipAddresses.map(ip => {
        const statusBadge = ip.is_blocked ? 
            '<span class="badge bg-danger">Blocked</span>' : 
            '<span class="badge bg-success">Active</span>';
        
        const suspiciousBadge = ip.suspicious_count > 0 ? 
            `<span class="badge bg-warning">${ip.suspicious_count}</span>` : 
            '<span class="badge bg-secondary">0</span>';
        
        const usernames = ip.usernames ? ip.usernames.split(',').join(', ') : 'No users';
        
        return `
            <tr class="${ip.is_blocked ? 'table-danger' : ''}">
                <td>
                    <a href="#" onclick="viewIpActivities('${ip.ip_address}'); return false;">
                        ${ip.ip_address}
                    </a>
                </td>
                <td>
                    <span class="badge bg-info">${ip.unique_users || 0}</span>
                    <small class="text-muted d-block">${usernames}</small>
                </td>
                <td><span class="badge bg-primary">${ip.request_count}</span></td>
                <td>${suspiciousBadge}</td>
                <td><small>${formatDateTime(ip.first_seen)}</small></td>
                <td><small>${formatDateTime(ip.last_seen)}</small></td>
                <td>${statusBadge}</td>
                <td>
                    ${ip.is_blocked ? 
                        `<button class="btn btn-sm btn-success" onclick="unblockIp('${ip.ip_address}')">
                            <i class="bi bi-check-circle"></i> Unblock
                        </button>` :
                        `<button class="btn btn-sm btn-danger" onclick="showBlockIpModal('${ip.ip_address}')">
                            <i class="bi bi-ban"></i> Block
                        </button>`
                    }
                </td>
            </tr>
        `;
    }).join('');
}

// Display IP pagination
function displayIpPagination(total, currentPage) {
    const pagination = document.getElementById('ipPagination');
    const totalPages = Math.ceil(total / 50);
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    
    html += `
        <li class="page-item ${currentPage === 0 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="loadIpAddresses(${currentPage - 1}); return false;">Previous</a>
        </li>
    `;
    
    for (let i = 0; i < Math.min(totalPages, 10); i++) {
        html += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="loadIpAddresses(${i}); return false;">${i + 1}</a>
            </li>
        `;
    }
    
    html += `
        <li class="page-item ${currentPage >= totalPages - 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="loadIpAddresses(${currentPage + 1}); return false;">Next</a>
        </li>
    `;
    
    pagination.innerHTML = html;
}

// Load suspicious activities
async function loadSuspiciousActivities(page = 0) {
    currentSuspiciousPage = page;
    const tbody = document.getElementById('suspiciousTableBody');
    tbody.innerHTML = '<tr><td colspan="7" class="text-center"><div class="spinner-border" role="status"></div></td></tr>';
    
    const params = new URLSearchParams({
        offset: page * 50,
        limit: 50
    });
    
    try {
        const response = await fetch(`/api/activity/logs/suspicious?${params.toString()}`);
        const data = await response.json();
        
        displaySuspiciousActivities(data.activities);
        displaySuspiciousPagination(data.total, page);
        document.getElementById('suspiciousTotalCount').textContent = data.total;
    } catch (error) {
        console.error('Error loading suspicious activities:', error);
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-danger">Error loading suspicious activities</td></tr>';
    }
}

// Display suspicious activities
function displaySuspiciousActivities(activities) {
    const tbody = document.getElementById('suspiciousTableBody');
    
    if (activities.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No suspicious activities found</td></tr>';
        return;
    }
    
    tbody.innerHTML = activities.map(activity => {
        const statusBadge = getStatusBadge(activity.status_code);
        const userDisplay = activity.username ? 
            `<a href="/admin/users?search=${activity.telegram_id}">${activity.username}</a>` : 
            '<span class="text-muted">Guest</span>';
        
        return `
            <tr class="table-warning">
                <td><small>${formatDateTime(activity.created_at)}</small></td>
                <td>
                    <a href="#" onclick="viewIpActivities('${activity.ip_address}'); return false;">
                        ${activity.ip_address}
                    </a>
                </td>
                <td>${userDisplay}</td>
                <td><span class="badge bg-secondary">${activity.method}</span></td>
                <td><small>${activity.endpoint}</small></td>
                <td>${statusBadge}</td>
                <td>
                    <button class="btn btn-sm btn-outline-danger" onclick="showBlockIpModal('${activity.ip_address}')">
                        <i class="bi bi-ban"></i> Block IP
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// Display suspicious pagination
function displaySuspiciousPagination(total, currentPage) {
    const pagination = document.getElementById('suspiciousPagination');
    const totalPages = Math.ceil(total / 50);
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    
    html += `
        <li class="page-item ${currentPage === 0 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="loadSuspiciousActivities(${currentPage - 1}); return false;">Previous</a>
        </li>
    `;
    
    for (let i = 0; i < Math.min(totalPages, 10); i++) {
        html += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="loadSuspiciousActivities(${i}); return false;">${i + 1}</a>
            </li>
        `;
    }
    
    html += `
        <li class="page-item ${currentPage >= totalPages - 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="loadSuspiciousActivities(${currentPage + 1}); return false;">Next</a>
        </li>
    `;
    
    pagination.innerHTML = html;
}

// Show block IP modal
function showBlockIpModal(ipAddress) {
    currentBlockIpAddress = ipAddress;
    document.getElementById('blockIpAddress').textContent = ipAddress;
    document.getElementById('blockReason').value = '';
    new bootstrap.Modal(document.getElementById('blockIpModal')).show();
}

// Confirm block IP
async function confirmBlockIp() {
    const reason = document.getElementById('blockReason').value;
    
    try {
        const params = new URLSearchParams();
        if (reason) params.append('reason', reason);
        
        const response = await fetch(`/api/activity/ip-addresses/${currentBlockIpAddress}/block?${params.toString()}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('blockIpModal')).hide();
            showAlert('success', 'IP address blocked successfully');
            loadIpAddresses(currentIpPage);
            loadActivities(currentActivityPage);
        } else {
            showAlert('danger', 'Failed to block IP address');
        }
    } catch (error) {
        console.error('Error blocking IP:', error);
        showAlert('danger', 'Error blocking IP address');
    }
}

// Unblock IP
async function unblockIp(ipAddress) {
    if (!confirm(`Are you sure you want to unblock ${ipAddress}?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/activity/ip-addresses/${ipAddress}/unblock`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showAlert('success', 'IP address unblocked successfully');
            loadIpAddresses(currentIpPage);
            loadActivities(currentActivityPage);
        } else {
            showAlert('danger', 'Failed to unblock IP address');
        }
    } catch (error) {
        console.error('Error unblocking IP:', error);
        showAlert('danger', 'Error unblocking IP address');
    }
}

// View IP activities
function viewIpActivities(ipAddress) {
    // Set the IP filter and switch to activities tab
    document.getElementById('activitySearch').value = ipAddress;
    const activitiesTab = new bootstrap.Tab(document.getElementById('activities-tab'));
    activitiesTab.show();
    loadActivities(0);
}

// View activity details (placeholder for future implementation)
function viewActivityDetails(activityId) {
    // This could be expanded to show more detailed information
    showAlert('info', 'Activity details view coming soon');
}

// Helper function to get status badge
function getStatusBadge(statusCode) {
    let badgeClass = 'bg-secondary';
    
    if (statusCode >= 200 && statusCode < 300) {
        badgeClass = 'bg-success';
    } else if (statusCode >= 300 && statusCode < 400) {
        badgeClass = 'bg-info';
    } else if (statusCode >= 400 && statusCode < 500) {
        badgeClass = 'bg-warning';
    } else if (statusCode >= 500) {
        badgeClass = 'bg-danger';
    }
    
    return `<span class="badge ${badgeClass}">${statusCode}</span>`;
}

// Helper function to format date/time
function formatDateTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Helper function to show alerts
function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}
