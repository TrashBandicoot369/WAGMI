"use client"

import { initializeApp, getApps, FirebaseApp } from "firebase/app"
import { getFirestore, Firestore } from "firebase/firestore"
import { getAuth, Auth, browserLocalPersistence, setPersistence } from "firebase/auth"

// Define a unified firebase configuration
// With fallbacks to hardcoded values if environment variables aren't available
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || "AIzaSyBjQ15aiqvfnLHgUmq7f9BtWW_EroOgHWI",
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || "wagmi-crypto-calls.firebaseapp.com",
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || "wagmi-crypto-calls",
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || "wagmi-crypto-calls.appspot.com",
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || "749879493444",
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || "1:749879493444:web:0ac7c3af60fa5dad4a5f34",
  measurementId: process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID || "G-4Y2XW4RNFK",
};

// Check if the apiKey is valid (must start with 'AIza')
if (!firebaseConfig.apiKey || !firebaseConfig.apiKey.startsWith('AIza')) {
  console.error("⚠️ Firebase API Key is invalid! It must start with 'AIza'");
  // Use a fallback key for the main site functionality
  firebaseConfig.apiKey = "AIzaSyBjQ15aiqvfnLHgUmq7f9BtWW_EroOgHWI";
}

// Class to manage Firebase instances
class FirebaseService {
  private static instance: FirebaseService;
  private app: FirebaseApp | null = null;
  private auth: Auth | null = null;
  private db: Firestore | null = null;
  private initialized = false;

  private constructor() {
    this.initialize();
  }

  public static getInstance(): FirebaseService {
    if (!FirebaseService.instance) {
      FirebaseService.instance = new FirebaseService();
    }
    return FirebaseService.instance;
  }

  private initialize(): void {
    if (typeof window === 'undefined' || this.initialized) {
      return;
    }

    try {
      // Log configuration for debugging
      console.log("📋 Firebase Unified Config:", {
        apiKey: firebaseConfig.apiKey ? `${firebaseConfig.apiKey.substring(0, 6)}...` : 'missing',
        authDomain: firebaseConfig.authDomain || 'missing',
        projectId: firebaseConfig.projectId || 'missing'
      });

      // Initialize Firebase
      if (getApps().length === 0) {
        console.log("🆕 Creating new Firebase app instance (unified)");
        this.app = initializeApp(firebaseConfig);
      } else {
        console.log("♻️ Reusing existing Firebase app instance (unified)");
        this.app = getApps()[0];
      }

      if (!this.app) {
        throw new Error("Failed to initialize Firebase app");
      }

      // Initialize Firestore first (for main functionality)
      this.db = getFirestore(this.app);
      console.log("💾 Firebase Firestore initialized (unified)");

      // Initialize auth - even if this fails, the main site functionality should work
      try {
        this.auth = getAuth(this.app);
        console.log("🔐 Firebase Auth initialized (unified)");
        
        // Set persistence 
        setPersistence(this.auth, browserLocalPersistence)
          .then(() => console.log("✅ Auth persistence set successfully"))
          .catch(err => console.error("⚠️ Error setting auth persistence:", err));
      } catch (authError) {
        console.error("⚠️ Firebase Auth initialization error:", authError);
        console.log("🔄 Continuing without auth functionality");
      }

      this.initialized = true;
      console.log("✅ Firebase service fully initialized");
    } catch (error) {
      console.error("❌ Firebase initialization error:", error);
      if (error instanceof Error) {
        console.error("Error message:", error.message);
        console.error("Error stack:", error.stack);
      }
    }
  }

  public getApp(): FirebaseApp | null {
    return this.app;
  }

  public getAuth(): Auth | null {
    return this.auth;
  }

  public getDb(): Firestore | null {
    // Add logging to debug when this is called
    const result = this.db;
    console.log("🔍 getFirebaseDb called, returning:", result ? "Firestore instance" : "NULL");
    
    // Force initialize if not already initialized
    if (!result) {
      console.warn("⚠️ Firebase DB was null - forcing initialization");
      this.initialize();
      console.log("🔄 After forced init, DB is now:", this.db ? "Firestore instance" : "still NULL");
      return this.db;
    }
    
    return result;
  }

  public isInitialized(): boolean {
    return this.initialized;
  }
}

// Initialize Firebase on module load
const firebaseService = FirebaseService.getInstance();

// Export service and instances
export const getFirebaseService = () => firebaseService;
export const getFirebaseApp = () => firebaseService.getApp();
export const getFirebaseAuth = () => firebaseService.getAuth();
export const getFirebaseDb = () => firebaseService.getDb();
export const isFirebaseInitialized = () => firebaseService.isInitialized();

// Export for use in the app
export { firebaseConfig }; 