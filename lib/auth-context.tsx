"use client"

import { createContext, useContext, useEffect, useState } from "react"
import { 
  User, 
  onAuthStateChanged
} from "firebase/auth"
// Import from the unified service
import { getFirebaseAuth, isFirebaseInitialized } from "@/lib/firebase-unified"

interface AuthContextType {
  user: User | null
  loading: boolean
  isAuthReady: boolean
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  isAuthReady: false
})

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [isAuthReady, setIsAuthReady] = useState(false)

  useEffect(() => {
    const auth = getFirebaseAuth();
    if (!auth) {
      console.log("Waiting for Firebase Auth to initialize...");
      setLoading(true);
      setIsAuthReady(false);
      
      // Check again after a short delay
      const checkInterval = setInterval(() => {
        const authCheck = getFirebaseAuth();
        if (authCheck) {
          console.log("Firebase Auth is now available");
          clearInterval(checkInterval);
          setupAuthListener(authCheck);
        }
      }, 1000);
      
      return () => clearInterval(checkInterval);
    } else {
      setupAuthListener(auth);
    }
    
    function setupAuthListener(auth: any) {
      console.log("Setting up auth listener");
      setIsAuthReady(true);
      
      const unsubscribe = onAuthStateChanged(auth, (user) => {
        console.log("Auth state changed:", user?.email || "No user");
        setUser(user);
        setLoading(false);
      });
      
      return unsubscribe;
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, isAuthReady }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext); 