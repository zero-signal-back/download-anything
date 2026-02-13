let currentDownloadId = null;
let progressInterval = null;
let progressValue = 0;

const statusMessages = [
    'Initializing download...',
    'Fetching video information...',
    'Extracting download link...',
    'Processing video...',
    'Downloading content...',
    'Almost done...',
    'Finalizing download...'
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
    const format = document.getElementById('formatSelect').value;
    const statusDiv = document.getElementById('status');
    const progressDiv = document.getElementById('progress');
    const downloadBtn = document.getElementById('downloadBtn');
    
    // Remove old preview if any
    const oldPreview = document.querySelector('.video-preview-section');
    if (oldPreview) oldPreview.remove();
    
    if (!url) {
        showStatus('Please enter a URL', 'error');
        return;
    }
    
    // Show ad before download
    showExoClickAd(() => {
        continueDownload(url, quality, format, statusDiv, progressDiv, downloadBtn);
    });
}

async function continueDownload(url, quality, format, statusDiv, progressDiv, downloadBtn) {
    const audio_only = (format === 'audio');
    
    downloadBtn.disabled = true;
    downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    statusDiv.className = 'status processing';
    statusDiv.textContent = audio_only ? '⏳ Extracting audio...' : '⏳ Getting video info...';
    statusDiv.classList.remove('hidden');
    progressDiv.classList.remove('hidden');
    
    // Reset and start progress animation
    progressValue = 0;
    messageIndex = 0;
    progressInterval = setInterval(updateProgressAnimation, 1500);
    updateProgressAnimation();
    
    try {
        // First, try to get direct video URL without downloading
        const infoResponse = await fetch('/get-video-info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url, quality })
        });
        
        const infoData = await infoResponse.json();
        
        // If we got direct URL, show video immediately
        if (infoData.direct_url && !audio_only) {
            clearInterval(progressInterval);
            progressValue = 100;
            document.querySelector('.progress-percentage').textContent = '100%';
            document.querySelector('.progress-fill').style.width = '100%';
            
            showStatus('✅ Video ready!', 'success');
            progressDiv.classList.add('hidden');
            downloadBtn.disabled = false;
            downloadBtn.innerHTML = '<span class="btn-text">Download Now</span><span class="btn-icon"><i class="fas fa-download"></i></span>';
            
            // Show video player immediately with direct URL
            const previewDiv = document.createElement('div');
            previewDiv.className = 'video-preview-section';
            previewDiv.innerHTML = `
                <div class="video-player-container">
                    <h3><i class="fas fa-play-circle"></i> Video Preview</h3>
                    <video controls autoplay class="video-player">
                        <source src="${infoData.direct_url}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                </div>
                <div class="download-actions">
                    <a href="${infoData.direct_url}" download class="download-final-btn">
                        <i class="fas fa-download"></i> Download Video
                    </a>
                    <button onclick="location.reload()" class="new-download-btn">
                        <i class="fas fa-plus"></i> Download Another
                    </button>
                </div>
            `;
            statusDiv.after(previewDiv);
            return;
        }
        
        // If no direct URL or audio format, proceed with server download
    
    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url, quality, audio_only })
        });
        
        const data = await response.json();
        
        if (data.error) {
            showStatus('❌ ' + data.error, 'error');
            downloadBtn.disabled = false;
            downloadBtn.innerHTML = '<span class="btn-text">Download Now</span><span class="btn-icon"><i class="fas fa-download"></i></span>';
            progressDiv.classList.add('hidden');
            clearInterval(progressInterval);
            return;
        }
        
        currentDownloadId = data.download_id;
        checkStatus(currentDownloadId);
        
    } catch (error) {
        showStatus('❌ Error: ' + error.message, 'error');
        downloadBtn.disabled = false;
        downloadBtn.innerHTML = '<span class="btn-text">Download Now</span><span class="btn-icon"><i class="fas fa-download"></i></span>';
        progressDiv.classList.add('hidden');
        clearInterval(progressInterval);
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
            
            showStatus('✅ Download completed successfully!', 'success');
            progressDiv.classList.add('hidden');
            downloadBtn.disabled = false;
            downloadBtn.innerHTML = '<span class="btn-text">Download Now</span><span class="btn-icon"><i class="fas fa-download"></i></span>';
            
            // Check if it's a video file
            const videoExtensions = ['.mp4', '.mkv', '.webm', '.avi', '.mov', '.flv'];
            const isVideo = videoExtensions.some(ext => data.file.toLowerCase().endsWith(ext));
            
            // Show video player with download button
            const previewDiv = document.createElement('div');
            previewDiv.className = 'video-preview-section';
            
            if (isVideo) {
                previewDiv.innerHTML = `
                    <div class="video-player-container">
                        <h3><i class="fas fa-play-circle"></i> Video Preview</h3>
                        <video controls autoplay class="video-player">
                            <source src="/file/${data.file}" type="video/mp4">
                            Your browser does not support the video tag.
                        </video>
                    </div>
                    <div class="download-actions">
                        <a href="/file/${data.file}" download class="download-final-btn">
                            <i class="fas fa-download"></i> Download Video
                        </a>
                        <button onclick="location.reload()" class="new-download-btn">
                            <i class="fas fa-plus"></i> Download Another
                        </button>
                    </div>
                `;
            
            statusDiv.after(previewDiv);
            } else {
                previewDiv.innerHTML = `
                    <div class="file-ready-container">
                        <div class="file-icon"><i class="fas fa-file-download"></i></div>
                        <h3>File Ready!</h3>
                        <p>Your file is ready to download</p>
                    </div>
                    <div class="download-actions">
                        <a href="/file/${data.file}" download class="download-final-btn">
                            <i class="fas fa-download"></i> Download File
                        </a>
                        <a href="/file/${data.file}" target="_blank" class="preview-final-btn">
                            <i class="fas fa-eye"></i> Preview
                        </a>
                        <button onclick="location.reload()" class="new-download-btn">
                            <i class="fas fa-plus"></i> Download Another
                        </button>
                    </div>
                `;
            }
            
            statusDiv.after(previewDiv);
            
        } else if (data.status === 'error') {
            clearInterval(progressInterval);
            showStatus('❌ Error: ' + data.message, 'error');
            progressDiv.classList.add('hidden');
            downloadBtn.disabled = false;
            downloadBtn.innerHTML = '<span class="btn-text">Download Now</span><span class="btn-icon"><i class="fas fa-download"></i></span>';
            
        } else if (data.status === 'processing') {
            statusDiv.textContent = '⏳ Downloading... Please wait';
            setTimeout(() => checkStatus(downloadId), 2000);
            
        } else {
            clearInterval(progressInterval);
            showStatus('⚠️ Unknown status', 'error');
            progressDiv.classList.add('hidden');
            downloadBtn.disabled = false;
            downloadBtn.innerHTML = '<span class="btn-text">Download Now</span><span class="btn-icon"><i class="fas fa-download"></i></span>';
        }
        
    } catch (error) {
        clearInterval(progressInterval);
        showStatus('❌ Error checking status: ' + error.message, 'error');
        progressDiv.classList.add('hidden');
        downloadBtn.disabled = false;
        downloadBtn.innerHTML = '<span class="btn-text">Download Now</span><span class="btn-icon"><i class="fas fa-download"></i></span>';
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

// ExoClick Interstitial Ad Counter
let adClickCount = parseInt(localStorage.getItem('adClickCount') || '0');

function showExoClickAd(callback) {
    adClickCount++;
    localStorage.setItem('adClickCount', adClickCount.toString());
    
    // Show ad every 2nd click
    if (adClickCount % 2 === 0) {
        // Trigger ExoClick interstitial
        if (typeof ExoLoader !== 'undefined') {
            ExoLoader.serve({"zone": "YOUR_ZONE_ID_HERE"});
        }
        // Wait 3 seconds then continue
        setTimeout(callback, 3000);
    } else {
        callback();
    }
}

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
