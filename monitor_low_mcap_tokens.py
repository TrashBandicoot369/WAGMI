import asyncio
import time
import datetime
from lib.firebase_admin_setup import db
from lib.tokenResolver import resolve_token_metadata
from google.cloud import firestore

# Use the db from firebase_admin_setup
calls_ref = db.collection("calls")

# Dictionary to track tokens that have dropped below 4k market cap
# Format: {token_id: {'timestamp': time_first_detected, 'symbol': symbol, 'contract': contract}}
low_mcap_tokens = {}

# Threshold values
MCAP_THRESHOLD = 4000  # $4k market cap threshold
TIME_THRESHOLD = 20 * 60  # 20 minutes in seconds

async def get_all_tokens():
    """Fetch all tokens from the database"""
    print("🔍 Fetching all tokens from the database...")
    docs = calls_ref.stream()
    return list(docs)

async def check_token_market_cap(doc_id, doc_data):
    """Check a token's current market cap and track if below threshold"""
    contract = doc_data.get("contract") or doc_data.get("contractAddress")
    symbol = doc_data.get("symbol", "UNKNOWN")
    
    if not contract:
        print(f"⚠️ Missing contract address for doc: {doc_id}")
        return
    
    # Get current market cap from Dexscreener
    token_metadata = await resolve_token_metadata(contract, db)
    
    if not token_metadata:
        print(f"⚠️ Could not retrieve metadata for {symbol} ({contract})")
        return
    
    # Parse market cap safely
    try:
        market_cap = token_metadata.get("marketCap", "UNKNOWN")
        if market_cap == "UNKNOWN":
            print(f"⚠️ Unknown market cap for {symbol} ({contract})")
            return
            
        if isinstance(market_cap, str):
            market_cap = float(market_cap)
    except (ValueError, TypeError):
        print(f"⚠️ Could not parse market cap value for {symbol}: {token_metadata.get('marketCap')}")
        return
    
    current_time = time.time()
    
    # Check if market cap is below threshold
    if market_cap < MCAP_THRESHOLD:
        print(f"📉 {symbol} market cap is below ${MCAP_THRESHOLD}: ${market_cap:,.2f}")
        
        # If token is not already being tracked, add it
        if doc_id not in low_mcap_tokens:
            low_mcap_tokens[doc_id] = {
                'timestamp': current_time,
                'symbol': symbol,
                'contract': contract
            }
            print(f"⏱️ Started tracking {symbol} at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        # If token is already being tracked, check duration
        else:
            duration = current_time - low_mcap_tokens[doc_id]['timestamp']
            minutes_passed = duration / 60
            
            if duration >= TIME_THRESHOLD:
                print(f"❌ REMOVING {symbol} - Market cap ${market_cap:,.2f} below threshold for {minutes_passed:.1f} minutes")
                
                # Delete the token
                await delete_token(doc_id)
                
                # Remove from tracking dictionary
                del low_mcap_tokens[doc_id]
            else:
                print(f"⏳ {symbol} below threshold for {minutes_passed:.1f} minutes (waiting for {TIME_THRESHOLD/60})")
    else:
        # If token was previously below threshold but now recovered, remove from tracking
        if doc_id in low_mcap_tokens:
            print(f"✅ {symbol} market cap recovered to ${market_cap:,.2f}, no longer tracking")
            del low_mcap_tokens[doc_id]

async def delete_token(doc_id):
    """Delete a token from the database"""
    try:
        # Delete from calls collection
        calls_ref.document(doc_id).delete()
        print(f"✅ Successfully deleted token with ID: {doc_id}")
        
        # Log deletion to a separate collection for audit purposes
        db.collection("deletedTokens").add({
            "originalId": doc_id,
            "reason": f"Market cap below ${MCAP_THRESHOLD} for {TIME_THRESHOLD/60} minutes",
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        
        return True
    except Exception as e:
        print(f"❌ Error deleting token {doc_id}: {e}")
        return False

async def monitor_tokens():
    """Main function to continuously monitor tokens"""
    print(f"🚀 Starting low market cap token monitor (threshold: ${MCAP_THRESHOLD:,.2f}, time: {TIME_THRESHOLD/60} minutes)")
    
    while True:
        try:
            tokens = await get_all_tokens()
            print(f"📊 Checking {len(tokens)} tokens...")
            
            for doc in tokens:
                doc_id = doc.id
                doc_data = doc.to_dict()
                await check_token_market_cap(doc_id, doc_data)
            
            # Print summary of currently tracked tokens
            if low_mcap_tokens:
                print("\n📋 Currently tracking these tokens below threshold:")
                for token_id, token_info in low_mcap_tokens.items():
                    duration = time.time() - token_info['timestamp']
                    print(f"  - {token_info['symbol']}: {duration/60:.1f} minutes (need {TIME_THRESHOLD/60})")
                print("")
            
            # Wait for 5 minutes before next check
            print(f"💤 Waiting 5 minutes before next check... ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
            await asyncio.sleep(5 * 60)  # 5 minutes
            
        except Exception as e:
            print(f"❌ Error in monitoring loop: {e}")
            await asyncio.sleep(60)  # Wait a minute and try again

if __name__ == "__main__":
    asyncio.run(monitor_tokens()) 