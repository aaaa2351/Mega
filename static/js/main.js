// Theme Management
document.addEventListener('DOMContentLoaded', function() {
    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    const savedColor = localStorage.getItem('color') || 'blue';
    
    document.body.setAttribute('data-theme', savedTheme);
    document.body.setAttribute('data-color', savedColor);
    
    // Theme toggle button
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.body.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            document.body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Update icon
            const icon = this.querySelector('i');
            icon.classList.toggle('fa-moon');
            icon.classList.toggle('fa-sun');
        });
    }
});

// File Upload Progress Animation
function updateUploadProgress(progressBar, progress) {
    progressBar.style.width = `${progress}%`;
    progressBar.setAttribute('aria-valuenow', progress);
    progressBar.textContent = `${progress}%`;
}

// Copy to Clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        alert('Copied to clipboard!');
    }).catch(function(err) {
        console.error('Failed to copy text: ', err);
    });
}

// Profile Picture Preview
function previewProfilePicture(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.querySelector('.profile-picture img').src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Form Validation
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('is-invalid');
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Password Strength Meter
function checkPasswordStrength(password) {
    let strength = 0;
    
    // Length check
    if (password.length >= 8) strength++;
    
    // Contains number
    if (/\d/.test(password)) strength++;
    
    // Contains letter
    if (/[a-zA-Z]/.test(password)) strength++;
    
    // Contains special character
    if (/[!@#$%^&*]/.test(password)) strength++;
    
    return strength;
}

// File Size Formatter
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Countdown Timer for File Expiry
function startExpiryCountdown(element, expiryDate) {
    const countdown = setInterval(() => {
        const now = new Date().getTime();
        const expiry = new Date(expiryDate).getTime();
        const distance = expiry - now;
        
        if (distance < 0) {
            clearInterval(countdown);
            element.textContent = 'Expired';
            return;
        }
        
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        
        element.textContent = `${days}d ${hours}h ${minutes}m`;
    }, 60000); // Update every minute
}

// Toast Notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast show toast-${type}`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="toast-header">
            <strong class="me-auto">${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">${message}</div>
    `;
    
    document.querySelector('.toast-container').appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// Search Users
function searchUsers(query) {
    fetch(`/search_users?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            const resultsContainer = document.getElementById('searchResults');
            resultsContainer.innerHTML = '';
            
            data.forEach(user => {
                const userElement = document.createElement('div');
                userElement.className = 'user-result';
                userElement.innerHTML = `
                    <img src="/static/img/${user.profile_picture}" class="rounded-circle" width="32" height="32">
                    <span>${user.username}</span>
                    <button class="btn btn-sm btn-primary share-with-user" data-user-id="${user.id}">
                        Share
                    </button>
                `;
                resultsContainer.appendChild(userElement);
            });
        });
}

// Initialize Tooltips and Popovers
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// File Upload Handling
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Dropzone if it exists
    if (typeof Dropzone !== 'undefined') {
        Dropzone.options.fileUpload = {
            paramName: "file",
            maxFilesize: 500, // MB
            acceptedFiles: ".jpg,.jpeg,.png,.gif,.pdf,.doc,.docx,.xls,.xlsx,.zip,.rar",
            init: function() {
                this.on("success", function(file, response) {
                    if (response.success) {
                        location.reload();
                    } else {
                        alert(response.error);
                    }
                });
                this.on("error", function(file, errorMessage) {
                    alert(errorMessage);
                });
            }
        };
    }

    // Share functionality
    document.querySelectorAll('.share-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const link = this.dataset.link;
            document.getElementById('shareLink').value = link;
            new bootstrap.Modal(document.getElementById('shareModal')).show();
        });
    });

    // Copy link functionality
    document.getElementById('copyLink')?.addEventListener('click', function() {
        const shareLink = document.getElementById('shareLink');
        shareLink.select();
        document.execCommand('copy');
        this.innerHTML = '<i class="fas fa-check"></i>';
        setTimeout(() => {
            this.innerHTML = '<i class="fas fa-copy"></i>';
        }, 2000);
    });

    // Delete file functionality
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            if (confirm('Are you sure you want to delete this file?')) {
                const fileId = this.dataset.fileId;
                fetch(`/delete_file/${fileId}`, {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.closest('tr').remove();
                    } else {
                        alert(data.error);
                    }
                });
            }
        });
    });

    // Share with user functionality
    document.getElementById('shareWithUser')?.addEventListener('click', function() {
        const username = document.getElementById('shareUsername').value;
        const fileId = document.getElementById('shareLink').dataset.fileId;
        
        fetch('/share_file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                file_id: fileId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('File shared successfully!');
                bootstrap.Modal.getInstance(document.getElementById('shareModal')).hide();
            } else {
                alert(data.error);
            }
        });
    });

    // Profile picture preview
    document.getElementById('profile_picture')?.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                document.querySelector('.profile-picture').src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });
});

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Confirm delete
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item?');
} 