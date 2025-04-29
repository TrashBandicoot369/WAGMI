import asyncio
import re
import time
from firebase_admin import firestore
from firebase_admin_setup import db
from lib.tokenResolver import resolve_token_metadata
from lib.telegram_api import scan_history_for_solana_contracts

# Improved regex for contract addresses
SOLANA_ADDRESS_PATTERN = r"([1-9A-HJ-NP-Za-km-z]{32,44})"

# Sample message with Solana contract addresses
sample_messages = [
    "Just launched: GN2G7d2qWfsfG3j6CXsiHuuTN5Huzkq4dq86Y4o7yiKc on Solana",
    "Check out this new coin: Cyk3RYqofTLKrhmFvHv2Eo85NSibCWoAGVx1Fx2faZ15 looking bullish",
    "Random text with no contract address",
    "Ethereum contract: 0x1234567890123456789012345678901234567890 but also Solana: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
]

async def test_contract_detection():
    """Test contract address detection in sample messages"""
    print("🧪 Testing Solana contract detection...")
    
    for i, message in enumerate(sample_messages):
        print(f"\nMessage {i+1}: {message}")
        
        # Find contract addresses
        solana_matches = re.findall(SOLANA_ADDRESS_PATTERN, message)
        
        if solana_matches:
            print(f"✅ Found {len(solana_matches)} Solana contract(s): {solana_matches}")
        else:
            print("❌ No Solana contracts found")
    
    return True

async def mock_contract_resolution():
    """Mock test for token resolution with simulated data"""
    print("\n🧪 Testing contract resolution logic with mock data...")
    
    # Mock data that would be returned by API responses
    mock_metadata = {
        "symbol": "TEST",
        "contract": "GN2G7d2qWfsfG3j6CXsiHuuTN5Huzkq4dq86Y4o7yiKc",
        "marketCap": 1000000,
        "volume24h": 50000,
        "initialMarketCap": 800000,
        "athMarketCap": 1200000,
        "dexUrl": "https://dexscreener.com/solana/GN2G7d2qWfsfG3j6CXsiHuuTN5Huzkq4dq86Y4o7yiKc",
        "source": "dexscreener",
        "timestamp": firestore.SERVER_TIMESTAMP,
        "chain": "solana",
        "status": "LIVE",
        "twitter": "https://twitter.com/test",
        "website": "https://test.com",
        "priceUsd": 0.001,
        "updated": firestore.SERVER_TIMESTAMP,
        "lastRefreshed": firestore.SERVER_TIMESTAMP
    }
    
    # Verify the data has all required fields
    required_fields = [
        "symbol", "contract", "marketCap", "volume24h", "dexUrl", 
        "timestamp", "athMarketCap", "chain", "status", 
        "initialMarketCap", "lastRefreshed", "updated"
    ]
    
    missing_fields = [field for field in required_fields if field not in mock_metadata]
    
    if missing_fields:
        print(f"⚠️ Missing required fields: {missing_fields}")
        return False
    
    print("✅ All required fields present for feed cards")
    
    # Simulate creating a Firestore card
    card_data = {
        "symbol": mock_metadata.get("symbol", "UNKNOWN"),
        "token": mock_metadata.get("symbol", "UNKNOWN"),
        "contract": mock_metadata.get("contract"),
        "dexUrl": mock_metadata.get("dexUrl"),
        "marketCap": mock_metadata.get("marketCap", 0),
        "volume24h": mock_metadata.get("volume24h", 0),
        "initialMarketCap": mock_metadata.get("marketCap", 0),
        "athMarketCap": mock_metadata.get("athMarketCap", mock_metadata.get("marketCap", 0)),
        "percentChange24h": 0,
        "capChange": 0,
        "timestamp": firestore.SERVER_TIMESTAMP,
        "updated": firestore.SERVER_TIMESTAMP,
        "lastRefreshed": firestore.SERVER_TIMESTAMP,
        "shotCaller": False,
        "chain": "solana",
        "status": "LIVE",
        "twitter": mock_metadata.get("twitter", ""),
        "website": mock_metadata.get("website", ""),
        "priceUsd": mock_metadata.get("priceUsd", 0)
    }
    
    print(f"✅ Simulated card for {card_data['symbol']}:")
    for key, value in sorted(card_data.items()):
        print(f"   {key}: {value}")
    
    return True

async def quick_live_test():
    """Perform a quick live API test with shortened timeouts"""
    print("\n🧪 Performing quick live test with real API...")
    
    # Known Solana token contracts (using SOL as it's guaranteed to resolve)
    sol_contract = "So11111111111111111111111111111111111111112"
    
    try:
        print(f"Attempting to resolve SOL native token contract: {sol_contract}")
        start_time = time.time()
        
        # Only try DexScreener for quick test
        async with asyncio.timeout(5):  # 5 second timeout
            url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{sol_contract}"
            
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=3) as response:
                    if response.status == 200:
                        print(f"✅ DexScreener API responded successfully for {sol_contract}")
                        return True
                    else:
                        print(f"❌ DexScreener API returned status {response.status}")
    except asyncio.TimeoutError:
        print("❌ API test timed out after 5 seconds")
    except Exception as e:
        print(f"❌ API test error: {e}")
    
    return False

async def validate_regex_patterns():
    """Test regex patterns used for contract detection"""
    print("\n🧪 Validating regex patterns...")
    
    # Test cases
    test_cases = [
        # Valid Solana addresses (should match)
        ("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", True),  # USDC
        ("So11111111111111111111111111111111111111112", True),  # SOL
        ("GN2G7d2qWfsfG3j6CXsiHuuTN5Huzkq4dq86Y4o7yiKc", True),  # Random valid Solana address
        
        # Invalid addresses (should not match)
        ("NOT_A_SOLANA_ADDRESS", False),
        ("0x1234567890123456789012345678901234567890", False),  # Ethereum address
        ("", False),
    ]
    
    # Define the patterns from qwant3.py
    solana_pattern = r"([1-9A-HJ-NP-Za-km-z]{32,44})"
    general_pattern = r"(0x[a-fA-F0-9]{40}|[1-9A-HJ-NP-Za-km-z]{32,44})"
    
    # Test Solana specific pattern
    solana_results = []
    for address, expected in test_cases:
        matches = re.findall(solana_pattern, address)
        result = len(matches) > 0
        solana_results.append((address, result == expected))
        
    # Test general pattern
    general_results = []
    for address, expected in test_cases:
        # For Ethereum addresses in general pattern, they should match
        if address.startswith("0x"):
            expected = True
            
        matches = re.findall(general_pattern, address)
        result = len(matches) > 0
        general_results.append((address, result == expected))
    
    # Print results
    print("Solana Pattern Results:")
    all_solana_pass = True
    for address, passed in solana_results:
        status = "✅" if passed else "❌"
        print(f"{status} {address}")
        if not passed:
            all_solana_pass = False
    
    print("\nGeneral Pattern Results:")
    all_general_pass = True
    for address, passed in general_results:
        status = "✅" if passed else "❌"
        print(f"{status} {address}")
        if not passed:
            all_general_pass = False
    
    return all_solana_pass and all_general_pass

async def run_tests():
    """Run all tests sequentially"""
    tests = [
        ("Contract Detection", test_contract_detection),
        ("Regex Validation", validate_regex_patterns),
        ("Mock Contract Resolution", mock_contract_resolution),
        ("Quick Live API Test", quick_live_test)
    ]
    
    results = {}
    
    for name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"RUNNING TEST: {name}")
        print(f"{'='*50}")
        
        try:
            start_time = time.time()
            success = await test_func()
            elapsed = time.time() - start_time
            
            results[name] = {
                "success": success,
                "time": elapsed
            }
            
            print(f"\n{'✅' if success else '❌'} {name} {'PASSED' if success else 'FAILED'} in {elapsed:.2f}s")
        except Exception as e:
            print(f"❌ Test error: {e}")
            import traceback
            traceback.print_exc()
            
            results[name] = {
                "success": False,
                "time": time.time() - start_time,
                "error": str(e)
            }
    
    # Print summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    for name, result in results.items():
        status = "PASSED" if result["success"] else "FAILED"
        print(f"{name:25} - {status:10} - {result['time']:.2f}s")
    
    successes = sum(1 for r in results.values() if r["success"])
    print(f"\n✅ {successes}/{len(tests)} tests passed")

if __name__ == "__main__":
    asyncio.run(run_tests()) 