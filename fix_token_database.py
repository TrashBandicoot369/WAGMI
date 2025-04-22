import asyncio
import aiohttp
from lib.firebase_admin_setup import db
from google.cloud import firestore

# Use the db from firebase_admin_setup
token_cache_ref = db.collection("tokenCache")
calls_ref = db.collection("calls")

async def resolve_token_from_dexscreener(contract_address):
    """
    Fetch token data directly from Dexscreener API without any custom mappings
    """
    url = f"https://api.dexscreener.com/latest/dex/search?q={contract_address}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as res:
                print(f"🚀 Dexscreener API status: {res.status}")
                if res.status == 200:
                    data = await res.json()
                    pairs = data.get("pairs", [])
                    
                    # Find pair matching our contract
                    matching_pair = None
                    for pair in pairs:
                        base_token = pair.get("baseToken", {})
                        if base_token.get("address", "").lower() == contract_address.lower():
                            matching_pair = pair
                            break
                    
                    # Use first pair if no exact match
                    if not matching_pair and pairs:
                        matching_pair = pairs[0]
                    
                    if matching_pair:
                        base_token = matching_pair.get("baseToken", {})
                        
                        # Get Twitter URL if available
                        twitter_url = None
                        info = matching_pair.get("info", {})
                        socials = info.get("socials", [])
                        
                        if isinstance(socials, list):
                            for social in socials:
                                if social.get("type") == "twitter":
                                    twitter_url = social.get("url")
                                    break
                        elif isinstance(socials, dict) and socials.get("twitter"):
                            twitter_url = socials.get("twitter")
                            
                        # Return token data
                        return {
                            "symbol": base_token.get("symbol", "UNKNOWN"),
                            "name": base_token.get("name", "UNKNOWN"),
                            "marketCap": matching_pair.get("marketCap", "UNKNOWN"),
                            "volume24h": matching_pair.get("volume", {}).get("h24", "UNKNOWN"),
                            "price": matching_pair.get("priceUsd", "UNKNOWN"),
                            "dexUrl": matching_pair.get("url", f"https://dexscreener.com/search?q={contract_address}"),
                            "twitter": twitter_url,
                            "contract": contract_address,
                        }
    except Exception as e:
        print(f"❌ Error fetching from Dexscreener: {e}")
        
    # Return default values if API call fails
    return {
        "symbol": "UNKNOWN",
        "name": "UNKNOWN",
        "marketCap": "UNKNOWN",
        "volume24h": "UNKNOWN",
        "price": "UNKNOWN",
        "dexUrl": f"https://dexscreener.com/search?q={contract_address}",
        "twitter": None,
        "contract": contract_address,
    }

async def fix_token_database():
    print("🔎 Scanning the database for tokens to update...")
    
    # Get all cached tokens
    all_cached_tokens = list(token_cache_ref.stream())
    print(f"Found {len(all_cached_tokens)} tokens in cache")
    
    for token_doc in all_cached_tokens:
        contract_address = token_doc.id
        print(f"🔄 Processing token: {contract_address}")
        
        # Get fresh data directly from Dexscreener
        token_data = await resolve_token_from_dexscreener(contract_address)
        
        if token_data.get("symbol") != "UNKNOWN":
            print(f"✅ Got data from Dexscreener: {token_data['symbol']}")
            
            # Update token cache
            token_cache_ref.document(contract_address).set({
                "symbol": token_data["symbol"],
                "name": token_data["name"],
                "marketCap": token_data["marketCap"],
                "volume24h": token_data["volume24h"],
                "price": token_data["price"],
                "dexUrl": token_data["dexUrl"],
                "twitter": token_data["twitter"],
                "timestamp": firestore.SERVER_TIMESTAMP
            })
            
            # Find and update all calls using this contract
            calls_query = calls_ref.where("contract", "==", contract_address).stream()
            for call in calls_query:
                call_update_data = {
                    "symbol": token_data["symbol"],
                    "marketCap": token_data["marketCap"],
                    "volume24h": token_data["volume24h"],
                    "twitter": token_data["twitter"],
                    "dexUrl": token_data["dexUrl"],
                    "updated": firestore.SERVER_TIMESTAMP,
                    "timestamp": firestore.SERVER_TIMESTAMP
                }
                call.reference.set(call_update_data, merge=True)
                print(f"✅ Updated call {call.id}")
            
            # Also check calls using contractAddress (old schema)
            old_calls_query = calls_ref.where("contractAddress", "==", contract_address).stream()
            for call in old_calls_query:
                old_call_update_data = {
                    "symbol": token_data["symbol"],
                    "token": token_data["symbol"], # For backward compatibility
                    "marketCap": token_data["marketCap"],
                    "volume24h": token_data["volume24h"],
                    "volume": token_data["volume24h"], # For backward compatibility
                    "twitter": token_data["twitter"],
                    "dexUrl": token_data["dexUrl"],
                    "updated": firestore.SERVER_TIMESTAMP,
                    "timestamp": firestore.SERVER_TIMESTAMP
                }
                call.reference.set(old_call_update_data, merge=True)
                print(f"✅ Updated old-schema call {call.id}")
        else:
            print(f"❌ Could not get data for {contract_address} from Dexscreener")
    
    print("✅ Database update complete")

if __name__ == "__main__":
    asyncio.run(fix_token_database()) 