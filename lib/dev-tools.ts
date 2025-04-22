"use client"

import { createUserWithEmailAndPassword } from "firebase/auth";
import { auth } from "./firebase-client";

// This file contains development tools only - NEVER use in production

/**
 * Creates a test admin user from the browser console
 * Usage: From your browser console, run:
 *   window.createTestAdminUser('your@email.com', 'password123')
 */
export function createTestAdminUser(email: string, password: string) {
  return createUserWithEmailAndPassword(auth, email, password)
    .then((userCredential) => {
      console.log("✅ Test user created successfully:", userCredential.user.email);
      return userCredential.user;
    })
    .catch((error) => {
      console.error("❌ Error creating test user:", error.code, error.message);
      throw error;
    });
}

// Expose function to window for console access
if (typeof window !== 'undefined') {
  (window as any).createTestAdminUser = createTestAdminUser;
} 