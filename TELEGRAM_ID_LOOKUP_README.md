# Telegram ID Lookup System

This document explains how to use the Telegram ID lookup system in the admin panel.

## Overview

The "Look up ID" feature allows you to quickly find a Telegram user's numeric ID by entering their username. This ID is required for adding users to the system.

## How It Works

1. When you enter a username and click "Look up ID", the system runs a Python script using Telethon to look up the real Telegram ID
2. If found, it fills in the ID automatically; if not, you'll need to get it manually with the Python script

## Requirements

To use the lookup feature, you need:

1. Python installed on your system
2. The Telethon library (`pip install telethon`)
3. A working internet connection

## Using the Lookup Feature

1. Enter the Telegram username (with or without the @ symbol)
2. Click "Look up ID"
3. Wait for the system to fetch the ID directly from Telegram
4. The ID will be automatically filled in if found

## Manual Lookup with Python Script

If the automatic lookup fails, you can use the Python script directly:

1. Open the `get_user_ids.py` script
2. Edit the usernames list to include the username you want to look up:
   ```python
   usernames = ["targetusername"]
   ```
3. Run the script:
   ```
   python get_user_ids.py
   ```
4. Copy the ID from the output:
   ```
   Username: @targetusername | User ID: 123456789
   ```
5. Enter this ID manually in the admin panel

## Troubleshooting

- If the lookup fails, check that you're using the correct username
- Make sure Python and Telethon are properly installed
- Check your internet connection
- Verify that the Telegram API credentials in the script are valid

## Security Note

The API keys in the Python script are for demonstration only. In a production environment, always use environment variables for sensitive credentials. 