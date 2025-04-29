import asyncio
import random
import time
from firebase_admin import firestore
from lib.firebase_admin_setup import db
from lib.tokenResolver import resolve_token_metadata

calls_ref = db.collection("calls")

async def update_token_with_retry(doc_ref, update_data, max_retries=3):
    """Update a token document with retry logic and backoff"""
    retry_count = 0
    token = update_data.get("symbol", "UNKNOWN")
    
    while retry_count < max_retries:
        try:
            # Add a small random delay to prevent write collisions (30-150ms)
            delay_ms = random.randint(30, 150)
            await asyncio.sleep(delay_ms / 1000)
            
            # Attempt to update using a transaction for atomicity
            transaction = db.transaction()
            
            @firestore.transactional
            def update_in_transaction(transaction, doc_ref, data):
                transaction.update(doc_ref, data)
            
            update_in_transaction(transaction, doc_ref, update_data)
            
            # Format changes for logging
            change_str = f"{update_data.get('percentChange24h', 0):+.2f}%" if 'percentChange24h' in update_data else "N/A"
            print(f"✅ Updated {token}: MC=${update_data.get('marketCap', 0)} ({change_str}), ATH=${update_data.get('athMarketCap', 0)}, Vol=${update_data.get('volume24h', 0)}")
            return True
        except Exception as e:
            retry_count += 1
            # Use exponential backoff with jitter
            backoff = (2 ** retry_count) + random.uniform(0, 1)
            print(f"⚠️ Firestore update failed for {token} (attempt {retry_count}/{max_retries}): {e}")
            if retry_count < max_retries:
                print(f"   Retrying in {backoff:.2f}s...")
                await asyncio.sleep(backoff)
            else:
                print(f"❌ Failed to update {token} after {max_retries} attempts")
                return False

async def refresh_all_tokens(limit_count: int = 50):
    """
    Refresh market data for tokens in Firestore (up to limit_count).
    Preserves ATH and updates percent changes.
    """
    start_time = time.time()
    print(f"🔄 Refreshing up to {limit_count} tokens...")

    all_calls = calls_ref.limit(limit_count).get()
    token_count = len(all_calls)
    print(f"Found {token_count} tokens to refresh")

    updated_count = 0
    error_count = 0
    ath_updated_count = 0
    skipped_count = 0

    def safe_number(value):
        if value is None:
            return 0
        if isinstance(value, (int, float)):
            return value
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0

    for index, doc in enumerate(all_calls):
        data = doc.to_dict()
        token = data.get("symbol") or data.get("token", "UNKNOWN")
        
        # Log progress
        print(f"[{index+1}/{token_count}] Processing {token}...")

        dex_url = data.get("dexUrl") or data.get("dexurl", "")
        if not dex_url:
            print(f"⚠️ Missing dexUrl for {token} (doc {doc.id}), skipping")
            skipped_count += 1
            continue

        contract = dex_url.split("/")[-1]
        if not contract:
            print(f"⚠️ Invalid dexUrl for {token}: {dex_url}")
            skipped_count += 1
            continue

        print(f"🔄 Refreshing {token} ({contract})...")

        current_market_cap = safe_number(data.get("marketCap", 0))
        ath_market_cap = safe_number(data.get("athMarketCap", 0))
        initial_market_cap = safe_number(data.get("initialMarketCap", 0))

        try:
            token_metadata = await resolve_token_metadata(contract, db, retries=2)
        except Exception as e:
            print(f"❌ Error resolving {token}: {e}")
            error_count += 1
            continue

        if not token_metadata or token_metadata.get("symbol", "UNKNOWN") == "UNKNOWN":
            print(f"❌ Could not resolve data for {token} ({contract})")
            error_count += 1
            continue

        new_market_cap = safe_number(token_metadata.get("marketCap", 0))
        volume_24h = safe_number(token_metadata.get("volume24h", 0))

        # Skip update if no meaningful change (saves Firestore writes)
        if (abs(new_market_cap - current_market_cap) / max(current_market_cap, 1) < 0.003 and 
            new_market_cap <= ath_market_cap):
            print(f"⏩ Skipping {token} - no significant change (MC: ${new_market_cap})")
            skipped_count += 1
            continue

        new_ath = max(ath_market_cap, new_market_cap)
        if new_market_cap > ath_market_cap:
            ath_updated_count += 1
            print(f"🏆 New ATH for {token}: ${new_market_cap}")

        percent_change = 0
        if current_market_cap > 0 and new_market_cap > 0:
            percent_change = ((new_market_cap - current_market_cap) / current_market_cap) * 100

        # Only set initialMarketCap if it doesn't exist yet
        # This preserves the original value and prevents overwriting with current market cap
        if initial_market_cap <= 0 and new_market_cap > 0:
            initial_market_cap = new_market_cap
            print(f"📊 Setting initial market cap for {token}: ${new_market_cap}")

        update_data = {
            "symbol": token_metadata.get("symbol"),
            "token": token_metadata.get("symbol"),
            "contract": contract,
            "dexUrl": f"https://dexscreener.com/solana/{contract}",
            "marketCap": new_market_cap,
            "volume24h": volume_24h,
            "volume": volume_24h,
            "athMarketCap": new_ath,
            "percentChange24h": percent_change,
            "capChange": percent_change,
            "lastRefreshed": firestore.SERVER_TIMESTAMP,
            "updated": firestore.SERVER_TIMESTAMP
        }

        # Only set initialMarketCap in the update if we need to (when it doesn't exist)
        if initial_market_cap > 0:
            update_data["initialMarketCap"] = initial_market_cap

        if token_metadata.get("twitter"):
            update_data["twitter"] = token_metadata.get("twitter")

        socials = {}
        if token_metadata.get("twitter"):
            socials["twitter"] = token_metadata.get("twitter")
        if token_metadata.get("website"):
            socials["website"] = token_metadata.get("website")
        if socials:
            update_data["socials"] = socials

        # Preserve important existing fields
        if "shotCaller" in data:
            update_data["shotCaller"] = data.get("shotCaller", False)

        if "timestamp" in data:
            update_data["timestamp"] = data.get("timestamp")
            
        if "forwarded" in data:
            update_data["forwarded"] = data.get("forwarded", False)
            
        if "forwardTimestamp" in data:
            update_data["forwardTimestamp"] = data.get("forwardTimestamp")

        # Update with retry logic
        success = await update_token_with_retry(doc.reference, update_data)
        if success:
            updated_count += 1
        else:
            error_count += 1

        # Add a small delay between processing tokens to prevent API rate limits
        await asyncio.sleep(random.uniform(0.5, 1.5))

    # Calculate execution time
    total_time = time.time() - start_time
    
    print(f"""
✅ Refresh complete in {total_time:.2f}s!
- Updated: {updated_count} tokens
- ATH updated: {ath_updated_count} tokens
- Skipped: {skipped_count} tokens
- Errors: {error_count} tokens
""")
    return updated_count, error_count, ath_updated_count, skipped_count

if __name__ == "__main__":
    print("🚀 Starting token refresh...")
    try:
        asyncio.run(refresh_all_tokens())
        print("✅ Done!")
    except KeyboardInterrupt:
        print("\n🛑 Refresh stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during refresh: {e}")
