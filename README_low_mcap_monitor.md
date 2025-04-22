# Low Market Cap Token Monitor

This script continuously monitors the market cap of tokens in the database and automatically removes any tokens that have a market cap below $4,000 for 20 minutes or longer.

## Features

- **Automatic Monitoring**: Checks all tokens in the database at regular intervals.
- **Threshold-Based Removal**: Removes tokens with market caps below $4,000 that remain below this threshold for at least 20 minutes.
- **Recovery Tracking**: If a token's market cap recovers above the threshold, it's removed from the tracking list.
- **Audit Log**: Creates records in a `deletedTokens` collection to keep track of removed tokens and the reason for removal.
- **Detailed Logging**: Provides comprehensive logs of all actions for monitoring and debugging.

## How It Works

1. Every 5 minutes, the script fetches all tokens from the database.
2. For each token, it retrieves the current market cap from Dexscreener API.
3. If a token's market cap is below $4,000, the script starts tracking it.
4. If a tracked token remains below the threshold for 20 minutes, it is deleted from the database.
5. If a tracked token's market cap recovers above the threshold, it is removed from the tracking list.

## Requirements

The script requires the same dependencies as other token-related scripts in the project:
- Python 3.7+
- Firebase Admin SDK
- `aiohttp` for async HTTP requests
- Access to the Dexscreener API

## Usage

Run the script to start monitoring:

```bash
python monitor_low_mcap_tokens.py
```

The script will run continuously, checking tokens every 5 minutes.

## Configuration

The script has two main configurable parameters:

- `MCAP_THRESHOLD`: Market cap threshold in USD (default: $4,000)
- `TIME_THRESHOLD`: Time in seconds a token must remain below the threshold to be removed (default: 20 minutes)

You can modify these values in the script to adjust the removal criteria.

## Integration with Existing Token Management

This script complements the existing token management scripts by adding automatic removal based on market cap thresholds. It can be run alongside other scripts like `refresh_all_tokens.py` without conflicts.

## Scheduling

For production use, it's recommended to set up this script to run automatically using a scheduling tool like cron or a cloud-based scheduler. 