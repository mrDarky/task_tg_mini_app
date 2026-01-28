// Task detail page functionality
const { getTelegramUser, getUserByTelegramId, apiRequest, showLoading, showSuccess, showError, openExternalLink } = window.miniApp;

let currentUser = null;
let currentTask = null;
let timer = null;
let timerSeconds = 0;
let timerRequired = 0;

// Get task ID from URL
function getTaskIdFromUrl() {
    const pathParts = window.location.pathname.split('/');
    return parseInt(pathParts[pathParts.length - 1]);
}

// Load task details
async function loadTaskDetail() {
    const tgUser = getTelegramUser();
    currentUser = await getUserByTelegramId(tgUser.id);
    
    const taskId = getTaskIdFromUrl();
    if (!taskId) {
        showError('Invalid task ID');
        return;
    }
    
    currentTask = await apiRequest(`/tasks/${taskId}`);
    
    if (!currentTask) {
        showError('Task not found');
        return;
    }
    
    displayTaskDetails();
    loadRelatedTasks();
}

// Display task details
function displayTaskDetails() {
    document.getElementById('taskTitle').textContent = currentTask.title;
    document.getElementById('taskType').textContent = currentTask.type.toUpperCase();
    document.getElementById('taskDescription').textContent = currentTask.description || 'Complete this task to earn stars';
    document.getElementById('taskReward').textContent = currentTask.reward;
    
    // Set task link
    const taskLink = document.getElementById('openTaskBtn');
    taskLink.href = currentTask.url || '#';
    
    // Display instructions
    displayInstructions();
    
    // Setup verification
    setupVerification();
    
    // Check if timer is needed (for video tasks)
    if (currentTask.type === 'youtube' && currentTask.url) {
        setupTimer();
    }
}

// Display step-by-step instructions
function displayInstructions() {
    const container = document.getElementById('taskSteps');
    
    let steps = [];
    
    switch (currentTask.type) {
        case 'youtube':
            steps = [
                'Click "Open Task Link" button',
                'Watch the video completely',
                'Wait for the timer to complete',
                'Take a screenshot of the video',
                'Submit the screenshot for verification'
            ];
            break;
        case 'tiktok':
            steps = [
                'Click "Open Task Link" button',
                'Like the TikTok video',
                'Follow the account (if required)',
                'Take a screenshot showing the like',
                'Submit the screenshot'
            ];
            break;
        case 'subscribe':
            steps = [
                'Click "Open Task Link" button',
                'Subscribe to the channel/page',
                'Enable notifications (if required)',
                'Take a screenshot of subscription',
                'Submit for verification'
            ];
            break;
        default:
            steps = ['Follow the task instructions', 'Complete the required action', 'Click "Mark as Complete"'];
    }
    
    container.innerHTML = steps.map((step, index) => `
        <div class="task-step">
            <div class="step-number">${index + 1}</div>
            <div>${step}</div>
        </div>
    `).join('');
}

// Setup verification requirements
function setupVerification() {
    const verificationText = document.getElementById('verificationText');
    const verificationSteps = document.getElementById('verificationSteps');
    
    if (currentTask.type === 'youtube' || currentTask.type === 'tiktok') {
        verificationText.textContent = 'Screenshot verification required for this task.';
        verificationSteps.innerHTML = `
            <div class="alert alert-info mb-0">
                <i class="bi bi-info-circle"></i>
                <strong>Required:</strong> Clear screenshot showing completion
            </div>
        `;
        
        // Show submission section
        document.getElementById('submissionSection').style.display = 'block';
    } else {
        verificationText.textContent = 'This task will be verified automatically.';
        document.getElementById('submissionSection').style.display = 'none';
    }
}

// Setup timer for video tasks
function setupTimer() {
    const timerSection = document.getElementById('timerSection');
    timerSection.style.display = 'block';
    
    // Estimate: 3 minutes for videos
    timerRequired = 180;
    timerSeconds = 0;
    
    updateTimerDisplay();
}

// Start timer
function startTimer() {
    if (timer) return; // Already running
    
    timer = setInterval(() => {
        timerSeconds++;
        updateTimerDisplay();
        
        if (timerSeconds >= timerRequired) {
            stopTimer();
            showSuccess('Timer completed! You can now submit the task.');
            document.getElementById('submitProofBtn').disabled = false;
        }
    }, 1000);
}

// Stop timer
function stopTimer() {
    if (timer) {
        clearInterval(timer);
        timer = null;
    }
}

// Update timer display
function updateTimerDisplay() {
    const minutes = Math.floor(timerSeconds / 60);
    const seconds = timerSeconds % 60;
    const display = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    document.getElementById('timerDisplay').textContent = display;
    
    const progress = (timerSeconds / timerRequired) * 100;
    document.getElementById('timerProgress').style.width = `${Math.min(progress, 100)}%`;
}

// Open task link and start timer
function openTaskLink() {
    openExternalLink(currentTask.url);
    
    if (currentTask.type === 'youtube') {
        startTimer();
    }
}

// Submit proof
async function submitProof() {
    const fileInput = document.getElementById('screenshotInput');
    
    if (!fileInput.files || fileInput.files.length === 0) {
        showError('Please select a screenshot');
        return;
    }
    
    // In a real app, this would upload the file
    showSuccess('Screenshot submitted for review!');
    
    // Simulate submission
    setTimeout(() => {
        window.location.href = '/miniapp/tasks';
    }, 2000);
}

// Mark task as complete (for auto-verify tasks)
async function markComplete() {
    if (!currentUser || !currentTask) return;
    
    try {
        const response = await apiRequest(`/users/${currentUser.id}/complete-task/${currentTask.id}`, {
            method: 'POST'
        });
        
        if (response) {
            showSuccess(`Task completed! You earned ${currentTask.reward} stars!`);
            setTimeout(() => {
                window.location.href = '/miniapp/tasks';
            }, 2000);
        }
    } catch (error) {
        showError('Failed to complete task');
    }
}

// Load related tasks
async function loadRelatedTasks() {
    const container = document.getElementById('relatedTasks');
    
    const tasks = await apiRequest(`/tasks?type=${currentTask.type}&status=active&limit=3`);
    
    if (tasks && tasks.length > 1) {
        // Filter out current task
        const relatedTasks = tasks.filter(t => t.id !== currentTask.id).slice(0, 2);
        
        if (relatedTasks.length > 0) {
            container.innerHTML = relatedTasks.map(task => window.miniApp.createTaskCard(task)).join('');
        } else {
            container.innerHTML = '<p class="text-muted">No related tasks</p>';
        }
    } else {
        container.innerHTML = '<p class="text-muted">No related tasks</p>';
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    loadTaskDetail();
    
    const openBtn = document.getElementById('openTaskBtn');
    if (openBtn) {
        openBtn.addEventListener('click', (e) => {
            e.preventDefault();
            openTaskLink();
        });
    }
    
    const completeBtn = document.getElementById('completeBtn');
    if (completeBtn) {
        completeBtn.addEventListener('click', markComplete);
    }
    
    const submitBtn = document.getElementById('submitProofBtn');
    if (submitBtn) {
        submitBtn.addEventListener('click', submitProof);
    }
});

// Cleanup timer on page unload
window.addEventListener('beforeunload', () => {
    stopTimer();
});
