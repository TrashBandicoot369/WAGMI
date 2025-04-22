// Import Firebase
const { initializeApp } = require('firebase/app');
const { getFirestore, collection, addDoc, serverTimestamp } = require('firebase/firestore');

// Hardcoded Firebase configuration to match your config
const firebaseConfig = {
  apiKey: "AIzaSyBjQ15aiqvfnLHgUmq7f9BtWW_EroOgHWI",
  authDomain: "wagmi-crypto-calls.firebaseapp.com",
  projectId: "wagmi-crypto-calls",
  storageBucket: "wagmi-crypto-calls.appspot.com",
  messagingSenderId: "749879493444",
  appId: "1:749879493444:web:0ac7c3af60fa5dad4a5f34",
  measurementId: "G-4Y2XW4RNFK"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

// Function to add a test call
async function addTestCall() {
  try {
    console.log('Adding test call to Firestore...');
    
    // Create a sample call document
    const testCall = {
      symbol: "TEST",
      token: "TEST",
      timestamp: serverTimestamp(),
      dexUrl: "https://dexscreener.com/ethereum/0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
      status: "LIVE",
      contractAddress: "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
      contract: "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
      marketCap: "1000000",
      volume24h: "500000",
      initialMarketCap: "900000",
      athMarketCap: "1100000",
      isNew: true
    };
    
    // Add the document to the 'calls' collection
    const docRef = await addDoc(collection(db, 'calls'), testCall);
    
    console.log('Test call added with ID:', docRef.id);
  } catch (error) {
    console.error('Error adding test call:', error);
  }
}

// Run the function
addTestCall(); 