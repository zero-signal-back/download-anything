# Telegram Private Channel Setup Guide

## Problem
Private Telegram channels (URLs with `/c/` like `https://t.me/c/1138977270/9500`) require authentication and cannot be downloaded without login.

## Solution
We've added **Telethon** library support for authenticated Telegram downloads.

## Setup Steps

### 1. Install Telethon
```bash
pip install telethon
```

### 2. Get Telegram API Credentials
1. Go to https://my.telegram.org/apps
2. Login with your phone number
3. Click "Create Application"
4. Fill in the form:
   - App title: Download Manager
   - Short name: dlmanager
   - Platform: Desktop
5. You'll get:
   - **API ID** (number like 12345678)
   - **API Hash** (string like "abcd1234efgh5678...")

### 3. Configure Credentials
Edit `telegram_config.py`:
```python
TELEGRAM_API_ID = "12345678"  # Your API ID
TELEGRAM_API_HASH = "abcd1234efgh5678..."  # Your API Hash
TELEGRAM_PHONE = "+911234567890"  # Your phone with country code
```

### 4. First Time Login
When you first download a private channel link:
1. System will send OTP to your Telegram
2. Enter the OTP code in terminal
3. Session will be saved for future use

### 5. Test
Try downloading: `https://t.me/c/1138977270/9500`

## How It Works
- **Public channels** (`https://t.me/channelname/123`) → Uses yt-dlp (no login needed)
- **Private channels** (`https://t.me/c/1234567/123`) → Uses Telethon (requires login)

## Features
✅ Download videos from private channels
✅ Download photos from private channels
✅ Download documents from private channels
✅ Session saved (login once, use forever)
✅ Automatic detection of private vs public

## Security Note
- Your API credentials are stored locally in `telegram_config.py`
- Session file `telegram_session.session` stores login
- Never share these files publicly
- Add to `.gitignore` if using Git

## Troubleshooting

**Error: "Telegram API credentials not configured"**
→ Edit `telegram_config.py` with your API credentials

**Error: "Message not found or you don't have access"**
→ Make sure you're a member of that private channel

**Error: "Phone number required"**
→ Add your phone number in `telegram_config.py`

## Alternative: Use Public Links
If you don't want to setup authentication, ask channel admin to:
1. Make channel public temporarily
2. Share public link format: `https://t.me/channelname/123`
