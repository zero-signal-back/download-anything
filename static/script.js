let currentDownloadId = null;
let progressInterval = null;
let progressValue = 0;

const statusMessages = [
    'Fetching video info...',
    'Extracting download link...',
    'Processing video...',
    'Downloading...',
    'Almost done...',
    'Finalizing...'
];

let messageIndex = 0;

function updateProgressAnimation() {
    const progressStatus = document.getElementById('progressStatus');
    const progressPercentage = document.querySelector('.progress-percentage');
    const progressFill = document.querySelector('.progress-fill');
    
    if (progressStatus) {
        messageIndex = (messageIndex + 1) % statusMessages.length;
        progressStatus.textContent = statusMessages[messageIndex];
    }
    
    // Smooth progress increment
    if (progressValue < 90) {
        progressValue += Math.floor(Math.random() * 8) + 3;
        if (progressValue > 90) progressValue = 90;
    }
    
    if (progressPercentage) {
        progressPercentage.textContent = `${progressValue}%`;
    }
    
    if (progressFill) {
        progressFill.style.width = `${progressValue}%`;
    }
}

async function startDownload() {
    const url = document.getElementById('urlInput').value.trim();
    const quality = document.getElementById('qualitySelect').value;
    const statusDiv = document.getElementById('status');
    const progressDiv = document.getElementById('progress');
    const downloadBtn = document.getElementById('downloadBtn');
    
    // Remove old preview buttons if any
    const oldPreview = document.querySelector('.preview-options');
    if (oldPreview) oldPreview.remove();
    
    if (!url) {
        showStatus('Please enter a URL', 'error');
        return;
    }
    
    downloadBtn.disabled = true;
    downloadBtn.textContent = 'Processing...';
    statusDiv.className = 'status processing';
    statusDiv.textContent = 'Starting download...';
    statusDiv.classList.remove('hidden');
    progressDiv.classList.remove('hidden');
    
    // Reset and start progress animation
    progressValue = 0;
    messageIndex = 0;
    progressInterval = setInterval(updateProgressAnimation, 1500);
    updateProgressAnimation();
    
    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url, quality })
        });
        
        const data = await response.json();
        
        if (data.error) {
            showStatus(data.error, 'error');
            downloadBtn.disabled = false;
            downloadBtn.textContent = 'Download';
            progressDiv.classList.add('hidden');
            return;
        }
        
        currentDownloadId = data.download_id;
        checkStatus(currentDownloadId);
        
    } catch (error) {
        showStatus('Error: ' + error.message, 'error');
        downloadBtn.disabled = false;
        downloadBtn.textContent = 'Download';
        progressDiv.classList.add('hidden');
    }
}

async function checkStatus(downloadId) {
    const statusDiv = document.getElementById('status');
    const progressDiv = document.getElementById('progress');
    const downloadBtn = document.getElementById('downloadBtn');
    
    try {
        const response = await fetch(`/status/${downloadId}`);
        const data = await response.json();
        
        if (data.status === 'completed') {
            clearInterval(progressInterval);
            progressValue = 100;
            document.querySelector('.progress-percentage').textContent = '100%';
            document.querySelector('.progress-fill').style.width = '100%';
            
            showStatus('✅ Download completed!', 'success');
            progressDiv.classList.add('hidden');
            downloadBtn.disabled = false;
            downloadBtn.textContent = 'Download';
            
            // Show preview option
            const previewDiv = document.createElement('div');
            previewDiv.className = 'preview-options';
            previewDiv.innerHTML = `
                <a href="/file/${data.file}" target="_blank" class="preview-btn">
                    <i class="fas fa-play-circle"></i> Preview/Play
                </a>
                <a href="/file/${data.file}" download class="download-btn-small">
                    <i class="fas fa-download"></i> Download
                </a>
            `;
            statusDiv.after(previewDiv);
            
        } else if (data.status === 'error') {
            clearInterval(progressInterval);
            showStatus('❌ Error: ' + data.message, 'error');
            progressDiv.classList.add('hidden');
            downloadBtn.disabled = false;
            downloadBtn.textContent = 'Download';
            
        } else if (data.status === 'processing') {
            statusDiv.textContent = '⏳ Downloading... Please wait';
            setTimeout(() => checkStatus(downloadId), 2000);
            
        } else {
            clearInterval(progressInterval);
            showStatus('Unknown status', 'error');
            progressDiv.classList.add('hidden');
            downloadBtn.disabled = false;
            downloadBtn.textContent = 'Download';
        }
        
    } catch (error) {
        clearInterval(progressInterval);
        showStatus('Error checking status: ' + error.message, 'error');
        progressDiv.classList.add('hidden');
        downloadBtn.disabled = false;
        downloadBtn.textContent = 'Download';
    }
}

function showStatus(message, type) {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = message;
    statusDiv.className = `status ${type}`;
    statusDiv.classList.remove('hidden');
}

// Enter key support
document.getElementById('urlInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        startDownload();
    }
});

// Username Search Functionality
async function searchUsername() {
    const username = document.getElementById('usernameInput').value.trim();
    const searchBtn = document.getElementById('searchBtn');
    const searchStatus = document.getElementById('searchStatus');
    const searchProgress = document.getElementById('searchProgress');
    const searchResults = document.getElementById('searchResults');
    const resultsList = document.getElementById('resultsList');
    
    if (!username) {
        showSearchStatus('Please enter a username', 'error');
        return;
    }
    
    if (username.length < 2 || username.length > 30) {
        showSearchStatus('Username must be 2-30 characters', 'error');
        return;
    }
    
    // Reset UI
    searchBtn.disabled = true;
    searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Searching...';
    searchStatus.classList.add('hidden');
    searchResults.classList.add('hidden');
    searchProgress.classList.remove('hidden');
    
    try {
        const response = await fetch('/search-username', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username })
        });
        
        const data = await response.json();
        
        if (data.error) {
            showSearchStatus(data.error, 'error');
            searchProgress.classList.add('hidden');
            searchBtn.disabled = false;
            searchBtn.innerHTML = '<i class="fas fa-search"></i> Search';
            return;
        }
        
        // Display results
        displaySearchResults(data);
        searchProgress.classList.add('hidden');
        searchBtn.disabled = false;
        searchBtn.innerHTML = '<i class="fas fa-search"></i> Search';
        
    } catch (error) {
        showSearchStatus('Error: ' + error.message, 'error');
        searchProgress.classList.add('hidden');
        searchBtn.disabled = false;
        searchBtn.innerHTML = '<i class="fas fa-search"></i> Search';
    }
}

function showSearchStatus(message, type) {
    const searchStatus = document.getElementById('searchStatus');
    searchStatus.textContent = message;
    searchStatus.className = `search-status ${type}`;
    searchStatus.classList.remove('hidden');
}

function displaySearchResults(data) {
    const searchResults = document.getElementById('searchResults');
    const resultsList = document.getElementById('resultsList');
    const resultsCount = document.querySelector('.results-count');
    
    if (data.found_count === 0) {
        showSearchStatus(`No profiles found for "${data.username}"`, 'error');
        return;
    }
    
    // Update count
    resultsCount.textContent = `${data.found_count} profiles found`;
    
    // Clear previous results
    resultsList.innerHTML = '';
    
    // Platform icons mapping
    const platformIcons = {
        'Instagram': 'fab fa-instagram',
        'Twitter': 'fab fa-twitter',
        'Facebook': 'fab fa-facebook',
        'TikTok': 'fab fa-tiktok',
        'YouTube': 'fab fa-youtube',
        'LinkedIn': 'fab fa-linkedin',
        'Snapchat': 'fab fa-snapchat',
        'Pinterest': 'fab fa-pinterest',
        'Reddit': 'fab fa-reddit',
        'Tumblr': 'fab fa-tumblr',
        'Medium': 'fab fa-medium',
        'Twitch': 'fab fa-twitch',
        'GitHub': 'fab fa-github',
        'GitLab': 'fab fa-gitlab',
        'Bitbucket': 'fab fa-bitbucket',
        'Stack Overflow': 'fab fa-stack-overflow',
        'Steam': 'fab fa-steam',
        'Discord': 'fab fa-discord',
        'Telegram': 'fab fa-telegram',
        'WhatsApp': 'fab fa-whatsapp',
        'Spotify': 'fab fa-spotify',
        'SoundCloud': 'fab fa-soundcloud',
        'Patreon': 'fab fa-patreon',
        'default': 'fas fa-user-circle'
    };
    
    // Create result cards
    data.found.forEach(result => {
        const card = document.createElement('div');
        card.className = 'result-card';
        
        const icon = platformIcons[result.platform] || platformIcons['default'];
        
        card.innerHTML = `
            <div class="result-icon">
                <i class="${icon}"></i>
            </div>
            <div class="result-info">
                <div class="result-platform">${result.platform}</div>
                <a href="${result.url}" target="_blank" class="result-link">${result.url}</a>
            </div>
            <div class="result-action">
                <a href="${result.url}" target="_blank" class="visit-btn">
                    <i class="fas fa-external-link-alt"></i>
                </a>
            </div>
        `;
        
        resultsList.appendChild(card);
    });
    
    searchResults.classList.remove('hidden');
}

// Enter key support for username search
document.getElementById('usernameInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        searchUsername();
    }
});
