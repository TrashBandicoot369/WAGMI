"use client"

import { useState } from "react"
import { searchTelegramUser, TelegramUserInfo } from "@/lib/telegram-api-clean"
import { doc, setDoc, serverTimestamp } from "firebase/firestore"
import { getFirebaseDb } from "@/lib/firebase-unified"

interface TelegramUserSearchProps {
  onUserAdded: () => void
}

export function TelegramUserSearch({ onUserAdded }: TelegramUserSearchProps) {
  const [searchUsername, setSearchUsername] = useState("")
  const [searching, setSearching] = useState(false)
  const [userFound, setUserFound] = useState<TelegramUserInfo | null>(null)
  const [role, setRole] = useState<"SHOT_CALLER" | "CALLER">("CALLER")
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)
    setUserFound(null)
    
    if (!searchUsername || searchUsername.length < 3) {
      setError("Please enter a valid username (min 3 characters)")
      return
    }
    
    setSearching(true)
    
    try {
      // Search for Telegram user
      const result = await searchTelegramUser(searchUsername)
      
      if (result.found) {
        setUserFound(result)
      } else {
        setError("User not found on Telegram")
      }
    } catch (err: any) {
      setError("Error searching for user: " + err.message)
      console.error("Telegram search error:", err)
    } finally {
      setSearching(false)
    }
  }

  const addUserToFirestore = async () => {
    if (!userFound || !userFound.id) {
      setError("No valid user found to add")
      return
    }
    
    setError(null)
    setSuccess(null)
    
    try {
      // Get Firestore DB from unified service
      const db = getFirebaseDb();
      if (!db) {
        setError("Firebase database is not initialized");
        return;
      }
      
      // Add user to Firestore
      const userId = String(userFound.id)
      const userDocRef = doc(db, "telegramUsers", userId)
      
      await setDoc(userDocRef, {
        username: userFound.username || "Unknown",
        role: role,
        addedBy: "admin-panel",
        addedAt: serverTimestamp()
      })
      
      setSuccess(`Added @${userFound.username} as ${role}`)
      setUserFound(null)
      setSearchUsername("")
      
      // Notify parent component that a user was added
      onUserAdded()
    } catch (err: any) {
      setError("Failed to add user: " + err.message)
      console.error("Error adding user:", err)
    }
  }

  return (
    <div className="bg-black/20 backdrop-blur-xl rounded-xl border border-white/10 p-6">
      <h2 className="text-xl font-bold text-white mb-4">Search Telegram User</h2>
      
      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={searchUsername}
            onChange={(e) => setSearchUsername(e.target.value)}
            placeholder="Enter username (without @)"
            className="flex-1 px-3 py-2 bg-black/40 border border-white/10 rounded-md text-white"
          />
          
          <button
            type="submit"
            disabled={searching}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md transition-colors disabled:opacity-50"
          >
            {searching ? "Searching..." : "Search"}
          </button>
        </div>
      </form>
      
      {error && (
        <div className="p-3 bg-red-500/20 border-l-4 border-red-500 text-white mb-4">
          {error}
        </div>
      )}
      
      {success && (
        <div className="p-3 bg-green-500/20 border-l-4 border-green-500 text-white mb-4">
          {success}
        </div>
      )}
      
      {userFound && (
        <div className="bg-gray-800/50 rounded-lg p-4 border border-white/10">
          <h3 className="text-lg font-medium text-white mb-2">User Found</h3>
          
          <div className="space-y-2 mb-4">
            <p className="text-gray-300">
              <span className="text-gray-400">ID:</span> {userFound.id}
            </p>
            <p className="text-gray-300">
              <span className="text-gray-400">Username:</span> @{userFound.username}
            </p>
            {userFound.first_name && (
              <p className="text-gray-300">
                <span className="text-gray-400">Name:</span> {userFound.first_name} {userFound.last_name || ""}
              </p>
            )}
          </div>
          
          <div className="flex items-end gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Role
              </label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value as "SHOT_CALLER" | "CALLER")}
                className="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-md text-white"
              >
                <option value="CALLER">CALLER</option>
                <option value="SHOT_CALLER">SHOT_CALLER</option>
              </select>
            </div>
            
            <button
              onClick={addUserToFirestore}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-md transition-colors"
            >
              Add User
            </button>
          </div>
        </div>
      )}
    </div>
  )
} 