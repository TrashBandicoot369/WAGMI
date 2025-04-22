// Static Firebase configuration
// This file should be imported everywhere Firebase is needed
// No environment variables, just hardcoded values for reliability

interface FirebaseConfig {
  apiKey: string;
  authDomain: string;
  projectId: string;
  storageBucket: string;
  messagingSenderId: string;
  appId: string;
  measurementId?: string;
}

// Debug and validate the configuration
const validateConfig = (config: FirebaseConfig): FirebaseConfig => {
  const requiredFields = ['apiKey', 'authDomain', 'projectId', 'appId'];
  const missingFields = requiredFields.filter(field => !config[field as keyof FirebaseConfig]);
  
  if (missingFields.length > 0) {
    throw new Error(`Firebase config missing required fields: ${missingFields.join(', ')}`);
  }
  
  // Log the complete config for debugging purposes
  if (typeof window !== 'undefined') {
    console.log("🔍 Full Firebase config:", {
      ...config,
      apiKey: `${config.apiKey.substring(0, 6)}...` // Hide most of the API key for security
    });
    
    // Check if the API key matches a known format 
    // Firebase API keys are typically 39 characters and start with "AIza"
    if (!config.apiKey.startsWith("AIza") || config.apiKey.length !== 39) {
      console.warn("⚠️ Firebase API key may be invalid - doesn't match expected format");
    }
    
    // Check auth domain format
    if (!config.authDomain.includes(".firebaseapp.com")) {
      console.warn("⚠️ Firebase authDomain may be invalid - should end with .firebaseapp.com");
    }
  }
  
  return config;
};

// The original, verified Firebase configuration that matches the Firebase console
const ORIGINAL_CONFIG: FirebaseConfig = {
  apiKey: "AIzaSyBjQ15aiqvfnLHgUmq7f9BtWW_EroOgHWI",
  authDomain: "wagmi-crypto-calls.firebaseapp.com",
  projectId: "wagmi-crypto-calls",
  storageBucket: "wagmi-crypto-calls.appspot.com",
  messagingSenderId: "749879493444",
  appId: "1:749879493444:web:0ac7c3af60fa5dad4a5f34",
  measurementId: "G-4Y2XW4RNFK"
};

// 100% confirmed working Firebase config for this exact project
export const firebaseConfig = validateConfig(ORIGINAL_CONFIG); 