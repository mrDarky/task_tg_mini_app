let currentPage = 0;
let currentSearch = '';
let currentStatus = '';
const limit = 20;

async function loadUsers() {
    try {
        const params = new URLSearchParams({
            skip: currentPage * limit,
            limit: limit
        });
        
        if (currentSearch) params.append('search', currentSearch);
        if (currentStatus) params.append('status', currentStatus);
        
        const response = await fetch(`/api/users?${params}`);
        const data = await response.json();
        
        displayUsers(data.users);
        updatePagination(data.total);
    } catch (error) {
        console.error('Error loading users:', error);
        showAlert('Error loading users', 'danger');
    }
}

function displayUsers(users) {
    const tbody = document.getElementById('users-table-body');
    
    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center">No users found</td></tr>';
        return;
    }
    
    tbody.innerHTML = users.map(user => `
        <tr>
            <td><input type="checkbox" class="user-checkbox" value="${user.id}"></td>
            <td>${user.id}</td>
            <td>${user.telegram_id}</td>
            <td>${user.username || 'N/A'}</td>
            <td><span class="badge bg-warning">${user.stars}</span></td>
            <td><span class="badge bg-${user.status === 'active' ? 'success' : 'danger'}">${user.status}</span></td>
            <td><span class="badge bg-info">${user.role}</span></td>
            <td>${formatDate(user.created_at)}</td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-primary" onclick="editUser(${user.id})">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-${user.status === 'active' ? 'danger' : 'success'}" 
                            onclick="${user.status === 'active' ? 'banUser' : 'unbanUser'}(${user.id})">
                        <i class="bi bi-${user.status === 'active' ? 'x-circle' : 'check-circle'}"></i>
                    </button>
                    <button class="btn btn-warning" onclick="adjustStars(${user.id})">
                        <i class="bi bi-star"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
    
    updateBulkButtons();
}

function updatePagination(total) {
    const totalPages = Math.ceil(total / limit);
    const pagination = document.getElementById('pagination');
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    
    if (currentPage > 0) {
        html += `<li class="page-item"><a class="page-link" href="#" onclick="changePage(${currentPage - 1}); return false;">Previous</a></li>`;
    }
    
    for (let i = 0; i < totalPages; i++) {
        if (i === currentPage) {
            html += `<li class="page-item active"><a class="page-link" href="#">${i + 1}</a></li>`;
        } else if (Math.abs(i - currentPage) < 3 || i === 0 || i === totalPages - 1) {
            html += `<li class="page-item"><a class="page-link" href="#" onclick="changePage(${i}); return false;">${i + 1}</a></li>`;
        } else if (Math.abs(i - currentPage) === 3) {
            html += `<li class="page-item disabled"><a class="page-link" href="#">...</a></li>`;
        }
    }
    
    if (currentPage < totalPages - 1) {
        html += `<li class="page-item"><a class="page-link" href="#" onclick="changePage(${currentPage + 1}); return false;">Next</a></li>`;
    }
    
    pagination.innerHTML = html;
}

function changePage(page) {
    currentPage = page;
    loadUsers();
}

async function editUser(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`);
        const user = await response.json();
        
        document.getElementById('edit-user-id').value = user.id;
        document.getElementById('edit-username').value = user.username || '';
        document.getElementById('edit-stars').value = user.stars;
        document.getElementById('edit-status').value = user.status;
        
        const modal = new bootstrap.Modal(document.getElementById('editUserModal'));
        modal.show();
    } catch (error) {
        console.error('Error loading user:', error);
        showAlert('Error loading user', 'danger');
    }
}

async function saveUser() {
    const userId = document.getElementById('edit-user-id').value;
    const data = {
        username: document.getElementById('edit-username').value,
        stars: parseInt(document.getElementById('edit-stars').value),
        status: document.getElementById('edit-status').value
    };
    
    try {
        const response = await fetch(`/api/users/${userId}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showAlert('User updated successfully', 'success');
            bootstrap.Modal.getInstance(document.getElementById('editUserModal')).hide();
            loadUsers();
        } else {
            showAlert('Error updating user', 'danger');
        }
    } catch (error) {
        console.error('Error saving user:', error);
        showAlert('Error saving user', 'danger');
    }
}

async function banUser(userId) {
    if (!confirm('Are you sure you want to ban this user?')) return;
    
    try {
        const response = await fetch(`/api/users/${userId}/ban`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showAlert('User banned successfully', 'success');
            loadUsers();
        } else {
            showAlert('Error banning user', 'danger');
        }
    } catch (error) {
        console.error('Error banning user:', error);
        showAlert('Error banning user', 'danger');
    }
}

async function unbanUser(userId) {
    try {
        const response = await fetch(`/api/users/${userId}/unban`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showAlert('User unbanned successfully', 'success');
            loadUsers();
        } else {
            showAlert('Error unbanning user', 'danger');
        }
    } catch (error) {
        console.error('Error unbanning user:', error);
        showAlert('Error unbanning user', 'danger');
    }
}

async function adjustStars(userId) {
    const delta = prompt('Enter stars to add (use negative numbers to subtract):');
    if (delta === null) return;
    
    const starsDelta = parseInt(delta);
    if (isNaN(starsDelta)) {
        showAlert('Invalid number', 'danger');
        return;
    }
    
    try {
        const response = await fetch(`/api/users/${userId}/adjust-stars?stars_delta=${starsDelta}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showAlert(`Stars adjusted by ${starsDelta}`, 'success');
            loadUsers();
        } else {
            showAlert('Error adjusting stars', 'danger');
        }
    } catch (error) {
        console.error('Error adjusting stars:', error);
        showAlert('Error adjusting stars', 'danger');
    }
}

function getSelectedUserIds() {
    const checkboxes = document.querySelectorAll('.user-checkbox:checked');
    return Array.from(checkboxes).map(cb => parseInt(cb.value));
}

function updateBulkButtons() {
    const selectedIds = getSelectedUserIds();
    const hasSelection = selectedIds.length > 0;
    
    document.getElementById('bulk-ban-btn').disabled = !hasSelection;
    document.getElementById('bulk-unban-btn').disabled = !hasSelection;
    document.getElementById('bulk-adjust-stars-btn').disabled = !hasSelection;
}

async function bulkBan() {
    const userIds = getSelectedUserIds();
    if (userIds.length === 0) return;
    
    if (!confirm(`Are you sure you want to ban ${userIds.length} users?`)) return;
    
    try {
        const response = await fetch('/api/users/bulk-update', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_ids: userIds,
                update_data: {status: 'banned'}
            })
        });
        
        if (response.ok) {
            showAlert(`${userIds.length} users banned`, 'success');
            loadUsers();
        } else {
            showAlert('Error in bulk operation', 'danger');
        }
    } catch (error) {
        console.error('Error in bulk ban:', error);
        showAlert('Error in bulk operation', 'danger');
    }
}

async function bulkUnban() {
    const userIds = getSelectedUserIds();
    if (userIds.length === 0) return;
    
    try {
        const response = await fetch('/api/users/bulk-update', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_ids: userIds,
                update_data: {status: 'active'}
            })
        });
        
        if (response.ok) {
            showAlert(`${userIds.length} users unbanned`, 'success');
            loadUsers();
        } else {
            showAlert('Error in bulk operation', 'danger');
        }
    } catch (error) {
        console.error('Error in bulk unban:', error);
        showAlert('Error in bulk operation', 'danger');
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    loadUsers();
    
    document.getElementById('search-btn').addEventListener('click', () => {
        currentSearch = document.getElementById('search-input').value;
        currentStatus = document.getElementById('status-filter').value;
        currentPage = 0;
        loadUsers();
    });
    
    document.getElementById('search-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            document.getElementById('search-btn').click();
        }
    });
    
    document.getElementById('select-all').addEventListener('change', (e) => {
        document.querySelectorAll('.user-checkbox').forEach(cb => {
            cb.checked = e.target.checked;
        });
        updateBulkButtons();
    });
    
    document.getElementById('users-table-body').addEventListener('change', (e) => {
        if (e.target.classList.contains('user-checkbox')) {
            updateBulkButtons();
        }
    });
    
    document.getElementById('save-user-btn').addEventListener('click', saveUser);
    document.getElementById('bulk-ban-btn').addEventListener('click', bulkBan);
    document.getElementById('bulk-unban-btn').addEventListener('click', bulkUnban);
    
    document.getElementById('bulk-adjust-stars-btn').addEventListener('click', async () => {
        const userIds = getSelectedUserIds();
        if (userIds.length === 0) return;
        
        const delta = prompt('Enter stars to add to all selected users:');
        if (delta === null) return;
        
        const starsDelta = parseInt(delta);
        if (isNaN(starsDelta)) {
            showAlert('Invalid number', 'danger');
            return;
        }
        
        for (const userId of userIds) {
            await fetch(`/api/users/${userId}/adjust-stars?stars_delta=${starsDelta}`, {
                method: 'POST'
            });
        }
        
        showAlert(`Stars adjusted for ${userIds.length} users`, 'success');
        loadUsers();
    });
});
