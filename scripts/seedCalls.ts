import { initializeApp } from "firebase/app"
import { getFirestore, collection, addDoc, Timestamp } from "firebase/firestore"

const firebaseConfig = {
  apiKey: "your-api-key",
  authDomain: "your-auth-domain",
  projectId: "your-project-id",
  storageBucket: "your-storage-bucket",
  messagingSenderId: "your-messaging-id",
  appId: "your-app-id"
}

const app = initializeApp(firebaseConfig)
const db = getFirestore(app)

const calls = [
  {
    token: "BONK",
    timestamp: Timestamp.fromDate(new Date("2025-04-17T16:20:00Z")),
    status: "LIVE",
    dexUrl: "https://dexscreener.com/solana/bonk",
  },
  {
    token: "PEPE2",
    timestamp: Timestamp.fromDate(new Date("2025-04-17T14:00:00Z")),
    status: "NEW",
    dexUrl: "https://dexscreener.com/ethereum/pepe2",
  },
  {
    token: "FLOKI",
    timestamp: Timestamp.fromDate(new Date("2025-04-17T12:00:00Z")),
    status: "COMPLETED",
    dexUrl: "https://dexscreener.com/eth/floki",
  },
  {
    token: "WOJAK",
    timestamp: Timestamp.fromDate(new Date("2025-04-17T10:00:00Z")),
    status: "LIVE",
    dexUrl: "https://dexscreener.com/eth/wojak",
  },
]

async function seed() {
  for (const call of calls) {
    await addDoc(collection(db, "calls"), call)
    console.log(`Added: ${call.token}`)
  }
  console.log("Seeding complete!")
}

seed().catch((error) => {
  console.error("Error seeding data:", error)
  process.exit(1)
}) 