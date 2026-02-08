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
