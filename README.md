# WAGMI Crypto Bots

This repository contains two Telegram bots for monitoring and processing crypto-related messages:

1. **Qwant3 Bot**: Monitors and processes messages from Qwant3
2. **WAGMI Calls Bot**: Monitors and processes WAGMI-related calls

## Project Structure

```
/
├── qwant3-bot/
│   ├── qwant3.py
│   ├── requirements.txt
│   └── serviceAccountKey.json
│
├── wagmicalls-bot/
│   ├── wagmicalls.py
│   ├── requirements.txt
│   └── serviceAccountKey.json
│
├── app/                      # Next.js app directory
├── components/              # React components
├── hooks/                   # Custom React hooks
├── lib/                     # Utility libraries
├── public/                  # Static assets
├── scripts/                 # Utility scripts
├── styles/                  # CSS styles
├── types/                   # TypeScript type definitions
│
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── firestore.rules         # Firestore security rules
├── next.config.mjs         # Next.js configuration
├── package.json            # Node.js dependencies
├── postcss.config.mjs      # PostCSS configuration
├── tailwind.config.ts      # Tailwind CSS configuration
├── tsconfig.json           # TypeScript configuration
│
├── *.py                    # Python utility scripts
│   ├── add_admin_roles_directly.py
│   ├── add_telegram_users.py
│   ├── check_firebase.py
│   ├── clear_firebase.py
│   ├── clear_firestore_collections.py
│   ├── clear_pump_cache.py
│   ├── clear_random_tokens.py
│   ├── delete_duplicate_tokens.py
│   ├── deploy_firestore_rules.py
│   ├── fix_invalid_timestamps.py
│   ├── fix_token_database.py
│   ├── fix_unknown_tokens.py
│   ├── forward_calls.py
│   ├── get_chat_ids.py
│   ├── get_group_ids.py
│   ├── get_user_ids.py
│   ├── get_usernames.py
│   ├── list_telegram_chats.py
│   ├── manage_telegram_users.py
│   ├── migrate_users_to_firestore.py
│   ├── monitor_low_mcap_tokens.py
│   ├── refresh_all_tokens.py
│   ├── refresh_pending_tokens.py
│   ├── refresh_unknowns.py
│   ├── rick_monitor.py
│   ├── sync_user_roles.py
│   ├── telegram_forward.py
│   └── watchdog.py
│
├── *.log                   # Log files
│   ├── rick_monitor.log
│   ├── wagmi_calls.log
│   └── wagmi_calls_detailed.log
│
├── *.session              # Telegram session files
│   ├── user_session.session
│   ├── user_session1.session
│   └── user_session2.session
│
├── *.md                   # Documentation
│   ├── ADMIN_PANEL_README.md
│   ├── README_low_mcap_monitor.md
│   ├── TELEGRAM_ID_LOOKUP_README.md
│   └── TELEGRAM_USERS_README.md
│
└── .gitignore            # Git ignore rules
```

## Features

### Qwant3 Bot
- Monitors specific Telegram groups for Qwant3 messages
- Parses token data from messages
- Stores parsed data in Firestore
- Prevents duplicate entries
- Comprehensive logging

### WAGMI Calls Bot
- Monitors WAGMI-related calls
- Processes and stores call data
- Integrates with Firebase for data persistence
- Comprehensive logging

## Requirements

- Python 3.8+
- Telethon
- Firebase Admin SDK
- Telegram API credentials
- aiohttp
- requests
- python-dotenv (optional, for local development)

## Setup

1. Install dependencies for each bot:
   ```
   cd qwant3-bot
   pip install -r requirements.txt
   
   cd ../wagmicalls-bot
   pip install -r requirements.txt
   ```

2. Make sure you have the Firebase service account key file (`serviceAccountKey.json`) in each bot's directory.

3. Run the bots:
   ```
   # For Qwant3 bot
   cd qwant3-bot
   python qwant3.py
   
   # For WAGMI Calls bot
   cd wagmicalls-bot
   python wagmicalls.py
   ```

## Configuration

Each bot uses the following environment variables which can be set in Railway dashboard:

- `API_ID` and `API_HASH`: Your Telegram API credentials
- `SESSION`: Telethon session name
- `SOURCE_GROUPS`: List of Telegram group IDs to monitor

## Logging

Each bot outputs logs to both the console and a dedicated log file:
- Qwant3 bot: `qwant3.log`
- WAGMI Calls bot: `wagmicalls.log`

## Deployment

Both bots are designed to be deployed on Railway. Each bot has its own directory with all necessary files for deployment.