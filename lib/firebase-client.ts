"use client"

import { initializeApp, getApps } from "firebase/app"
import { getFirestore } from "firebase/firestore"
import { getAuth } from "firebase/auth"

// Hardcoded Firebase configuration for client-side use
// We need to use hardcoded values since environment variables aren't properly loaded
const firebaseConfig = {
  apiKey: "AIzaSyBjQ15aiqvfnLHgUmq7f9BtWW_EroOgHWI",
  authDomain: "wagmi-crypto-calls.firebaseapp.com",
  projectId: "wagmi-crypto-calls",
  storageBucket: "wagmi-crypto-calls.appspot.com",
  messagingSenderId: "749879493444",
  appId: "1:749879493444:web:0ac7c3af60fa5dad4a5f34",
  measurementId: "G-4Y2XW4RNFK"
};

// Initialize Firebase with better error handling
let app;
try {
  if (getApps().length === 0) {
    console.log("🚀 Client: Initializing Firebase for the first time");
    app = initializeApp(firebaseConfig);
    console.log("✅ Client: Firebase initialized successfully");
  } else {
    console.log("♻️ Client: Firebase already initialized, reusing instance");
    app = getApps()[0];
  }
} catch (error) {
  console.error("❌ Client: Failed to initialize Firebase:", error);
  throw error;
}

// Export Firebase services
export const db = getFirestore(app);
export const auth = getAuth(app);

// Debug logging for client-side validation
console.log("📦 Client Firebase Auth API Key:", auth.app.options.apiKey); 