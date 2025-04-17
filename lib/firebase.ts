import { initializeApp, getApps } from "firebase/app"
import { getFirestore } from "firebase/firestore"

const firebaseConfig = {
  apiKey: "<your-api-key>",
  authDomain: "<your-auth-domain>",
  projectId: "<your-project-id>",
  storageBucket: "<your-storage-bucket>",
  messagingSenderId: "<your-messaging-id>",
  appId: "<your-app-id>"
}

// Initialize Firebase only on the client side and if it hasn't been initialized yet
let app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0]
export const db = typeof window !== 'undefined' ? getFirestore(app) : null 