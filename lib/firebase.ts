import { initializeApp, getApps } from "firebase/app"
import { getFirestore } from "firebase/firestore"

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || "<your-api-key>",
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || "<your-auth-domain>",
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || "<your-project-id>",
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || "<your-storage-bucket>",
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || "<your-messaging-id>",
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || "<your-app-id>"
}

const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0]
export const db = getFirestore(app) 