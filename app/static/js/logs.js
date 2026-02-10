// Logs page functionality
let allLogsOffset = 0;
let errorLogsOffset = 0;
const LIMIT = 1000;

// Load all logs
async function loadAllLogs(append = false) {
    try {
        const response = await fetch(`/api/logs/?offset=${allLogsOffset}&limit=${LIMIT}`);
        const data = await response.json();
        
        const tbody = document.getElementById('allLogsTableBody');
        
        if (!append) {
            tbody.innerHTML = '';
        }
        
        if (data.logs.length === 0 && !append) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">No logs found</td></tr>';
            document.getElementById('allLogsLoadMore').style.display = 'none';
            return;
        }
        
        data.logs.forEach(log => {
            const row = createLogRow(log);
            tbody.appendChild(row);
        });
        
        // Update count
        document.getElementById('allLogsCount').textContent = `${data.total} total logs`;
        
        // Show/hide load more button
        const loadMoreBtn = document.getElementById('allLogsLoadMore');
        if (data.total > allLogsOffset + LIMIT) {
            loadMoreBtn.style.display = 'block';
        } else {
            loadMoreBtn.style.display = 'none';
        }
        
    } catch (error) {
        console.error('Error loading all logs:', error);
        showAlert('Error loading logs', 'danger');
    }
}

// Load error logs
async function loadErrorLogs(append = false) {
    try {
        const response = await fetch(`/api/logs/errors?offset=${errorLogsOffset}&limit=${LIMIT}`);
        const data = await response.json();
        
        const tbody = document.getElementById('errorLogsTableBody');
        
        if (!append) {
            tbody.innerHTML = '';
        }
        
        if (data.logs.length === 0 && !append) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">No error logs found</td></tr>';
            document.getElementById('errorLogsLoadMore').style.display = 'none';
            return;
        }
        
        data.logs.forEach(log => {
            const row = createLogRow(log);
            tbody.appendChild(row);
        });
        
        // Update count
        document.getElementById('errorLogsCount').textContent = `${data.total} error logs`;
        
        // Show/hide load more button
        const loadMoreBtn = document.getElementById('errorLogsLoadMore');
        if (data.total > errorLogsOffset + LIMIT) {
            loadMoreBtn.style.display = 'block';
        } else {
            loadMoreBtn.style.display = 'none';
        }
        
    } catch (error) {
        console.error('Error loading error logs:', error);
        showAlert('Error loading error logs', 'danger');
    }
}

// Create log table row
function createLogRow(log) {
    const row = document.createElement('tr');
    
    // Format date
    const date = new Date(log.created_at);
    const formattedDate = date.toLocaleString();
    
    // Level badge
    let levelClass = 'bg-secondary';
    if (log.level === 'ERROR') levelClass = 'bg-danger';
    else if (log.level === 'CRITICAL') levelClass = 'bg-dark';
    else if (log.level === 'WARNING') levelClass = 'bg-warning text-dark';
    else if (log.level === 'INFO') levelClass = 'bg-info text-dark';
    
    const levelBadge = `<span class="badge ${levelClass}">${log.level}</span>`;
    
    // Truncate message for table display
    const truncatedMessage = log.message.length > 100 
        ? log.message.substring(0, 100) + '...' 
        : log.message;
    
    row.innerHTML = `
        <td>${formattedDate}</td>
        <td>${levelBadge}</td>
        <td>${log.source || '-'}</td>
        <td>${escapeHtml(truncatedMessage)}</td>
        <td>
            <button class="btn btn-sm btn-outline-primary" onclick="showLogDetail(${log.id}, '${log.level}', '${formattedDate}', '${escapeHtml(log.source || '-')}', \`${escapeHtml(log.message)}\`, \`${escapeHtml(log.traceback || '')}\`)">
                <i class="bi bi-eye"></i> View
            </button>
        </td>
    `;
    
    return row;
}

// Show log detail modal
function showLogDetail(id, level, time, source, message, traceback) {
    // Set level with appropriate badge
    const detailLevelSpan = document.getElementById('detailLevel');
    detailLevelSpan.textContent = level;
    detailLevelSpan.className = 'badge';
    
    if (level === 'ERROR') detailLevelSpan.classList.add('bg-danger');
    else if (level === 'CRITICAL') detailLevelSpan.classList.add('bg-dark');
    else if (level === 'WARNING') detailLevelSpan.classList.add('bg-warning', 'text-dark');
    else if (level === 'INFO') detailLevelSpan.classList.add('bg-info', 'text-dark');
    else detailLevelSpan.classList.add('bg-secondary');
    
    // Set other details
    document.getElementById('detailTime').textContent = time;
    document.getElementById('detailSource').textContent = source;
    document.getElementById('detailMessage').textContent = message;
    
    // Show/hide traceback
    const tracebackContainer = document.getElementById('detailTracebackContainer');
    if (traceback && traceback !== 'null' && traceback !== '') {
        tracebackContainer.style.display = 'block';
        document.getElementById('detailTraceback').textContent = traceback;
    } else {
        tracebackContainer.style.display = 'none';
    }
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('logDetailModal'));
    modal.show();
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Show alert message
function showAlert(message, type = 'success') {
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

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Load initial logs
    loadAllLogs();
    
    // Load more buttons
    document.getElementById('allLogsLoadMore').addEventListener('click', function() {
        allLogsOffset += LIMIT;
        loadAllLogs(true);
    });
    
    document.getElementById('errorLogsLoadMore').addEventListener('click', function() {
        errorLogsOffset += LIMIT;
        loadErrorLogs(true);
    });
    
    // Tab change events
    document.getElementById('error-logs-tab').addEventListener('shown.bs.tab', function() {
        if (errorLogsOffset === 0) {
            loadErrorLogs();
        }
    });
});
