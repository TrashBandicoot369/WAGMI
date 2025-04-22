"use client"

import { useState, useEffect } from "react"
import { collection, getDocs, query, orderBy, deleteDoc, doc, setDoc, serverTimestamp, where } from "firebase/firestore"
import { getFirebaseDb } from "@/lib/firebase-unified"
import { TelegramUserSearch } from "./telegram-user-search"

interface TelegramUser {
  id: string
  username: string
  role: "SHOT_CALLER" | "CALLER"
  addedBy: string
  addedAt: any // Firestore timestamp
}

export function TelegramUserManager() {
  const [users, setUsers] = useState<TelegramUser[]>([])
  const [loading, setLoading] = useState(true)
  const [addError, setAddError] = useState<string | null>(null)
  const [addSuccess, setAddSuccess] = useState<string | null>(null)
  const [telegramUsername, setTelegramUsername] = useState("")
  const [telegramId, setTelegramId] = useState("")
  const [selectedRole, setSelectedRole] = useState<"SHOT_CALLER" | "CALLER">("CALLER")

  const loadUsers = async () => {
    try {
      setLoading(true)
      
      const db = getFirebaseDb();
      if (!db) {
        console.error("Firestore not initialized");
        setAddError("Database not initialized");
        setLoading(false);
        return;
      }
      
      const rolesRef = collection(db, "roles")
      const q = query(rolesRef, orderBy("addedAt", "desc"))
      const querySnapshot = await getDocs(q)
      
      const fetchedUsers: TelegramUser[] = []
      querySnapshot.forEach((doc) => {
        const data = doc.data()
        // Normalize the role value to ensure it's either "CALLER" or "SHOT_CALLER"
        let normalizedRole: "CALLER" | "SHOT_CALLER" = "CALLER"
        if (data.role) {
          const roleUpper = data.role.toUpperCase()
          normalizedRole = roleUpper === "SHOT_CALLER" ? "SHOT_CALLER" : "CALLER"
        }
        
        fetchedUsers.push({
          id: doc.id,
          username: data.username || data.name || "Unknown",
          role: normalizedRole,
          addedBy: data.addedBy || "unknown",
          addedAt: data.addedAt ? new Date(data.addedAt.toDate()) : new Date()
        })
      })
      
      console.log("Fetched users:", fetchedUsers);
      setUsers(fetchedUsers)
    } catch (error) {
      console.error("Error loading users:", error)
      setAddError("Failed to load users")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadUsers()
  }, [])

  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!telegramUsername || !telegramId) {
      setAddError("Please enter both username and ID")
      return
    }
    
    try {
      const db = getFirebaseDb();
      if (!db) {
        setAddError("Database not initialized");
        return;
      }
      
      const userDocRef = doc(db, "roles", telegramId)
      await setDoc(userDocRef, {
        username: telegramUsername,
        name: telegramUsername, // Also set the name field for compatibility
        role: selectedRole,
        addedBy: "admin-panel",
        addedAt: serverTimestamp()
      })
      
      setAddSuccess(`Added @${telegramUsername} as ${selectedRole}`)
      setTelegramUsername("")
      setTelegramId("")
      
      // Reload users list
      loadUsers()
    } catch (error) {
      console.error("Error adding user:", error)
      setAddError("Failed to add user")
    }
  }

  const handleBulkAddUsers = async () => {
    const usersToAdd = [
      { id: "191059284", username: "bizonacci", role: "CALLER" },
      { id: "374435895", username: "j1legend", role: "CALLER" },
      { id: "1058653530", username: "le_printoor", role: "CALLER" },
      { id: "52381180", username: "ohcharlie", role: "CALLER" },
      { id: "1087968824", username: "alphameo", role: "CALLER" },
      { id: "1112693797", username: "sonder_crypto", role: "CALLER" },
      { id: "782123512", username: "amitysol", role: "CALLER" }
    ];
    
    try {
      const db = getFirebaseDb();
      if (!db) {
        setAddError("Database not initialized");
        return;
      }
      
      let addedCount = 0;
      
      for (const user of usersToAdd) {
        const userDocRef = doc(db, "roles", user.id);
        await setDoc(userDocRef, {
          username: user.username,
          name: user.username, // Also set the name field for compatibility
          role: user.role,
          addedBy: "admin-panel-bulk",
          addedAt: serverTimestamp()
        });
        addedCount++;
      }
      
      setAddSuccess(`Added ${addedCount} users successfully`);
      
      // Reload users list
      loadUsers();
    } catch (error) {
      console.error("Error bulk adding users:", error);
      setAddError("Failed to bulk add users");
    }
  };

  const handleDeleteUser = async (userId: string, username: string) => {
    if (!confirm(`Are you sure you want to delete @${username}?`)) {
      return
    }
    
    try {
      const db = getFirebaseDb();
      if (!db) {
        setAddError("Database not initialized");
        return;
      }
      
      await deleteDoc(doc(db, "roles", userId))
      setUsers(users.filter(user => user.id !== userId))
      setAddSuccess(`User @${username} deleted successfully`)
      
      // Reload users list
      loadUsers()
    } catch (error) {
      console.error("Error deleting user:", error)
      setAddError("Failed to delete user")
    }
  }

  const handleRoleChange = async (userId: string, username: string, newRole: "SHOT_CALLER" | "CALLER") => {
    try {
      const db = getFirebaseDb();
      if (!db) {
        setAddError("Database not initialized");
        return;
      }
      
      const userDocRef = doc(db, "roles", userId)
      await setDoc(userDocRef, { role: newRole }, { merge: true })
      
      // Update local state
      setUsers(users.map(user => 
        user.id === userId ? { ...user, role: newRole } : user
      ))
      
      setAddSuccess(`Changed @${username} role to ${newRole}`)
      
      // Reload users list to ensure UI shows latest data
      loadUsers()
    } catch (error) {
      console.error("Error updating role:", error)
      setAddError("Failed to update user role")
    }
  }

  return (
    <div className="space-y-8">
      <div className="bg-black/20 backdrop-blur-xl rounded-xl border border-white/10 p-6">
        <h2 className="text-xl font-bold text-white mb-4">Add Telegram User</h2>
        
        <form onSubmit={handleAddUser} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-200">
                Telegram ID
              </label>
              <input
                type="text"
                value={telegramId}
                onChange={(e) => setTelegramId(e.target.value)}
                className="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-md text-white"
                placeholder="12345678"
                required
              />
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-200">
                Username
              </label>
              <input
                type="text"
                value={telegramUsername}
                onChange={(e) => setTelegramUsername(e.target.value)}
                className="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-md text-white"
                placeholder="username (without @)"
                required
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-200">Role</label>
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value as "SHOT_CALLER" | "CALLER")}
              className="w-full px-3 py-2 bg-black/40 border border-white/10 rounded-md text-white"
            >
              <option value="CALLER">CALLER</option>
              <option value="SHOT_CALLER">SHOT_CALLER</option>
            </select>
          </div>
          
          {addError && <p className="text-red-500 text-sm">{addError}</p>}
          {addSuccess && <p className="text-green-500 text-sm">{addSuccess}</p>}
          
          <div className="flex flex-wrap gap-3">
            <button
              type="submit"
              className="py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md transition-colors"
            >
              Add User
            </button>
            
            <button
              type="button"
              onClick={handleBulkAddUsers}
              className="py-2 px-4 bg-green-600 hover:bg-green-700 text-white font-medium rounded-md transition-colors"
            >
              Add Specified Users
            </button>
          </div>
        </form>
      </div>
      
      <div className="bg-black/20 backdrop-blur-xl rounded-xl border border-white/10 p-6">
        <h2 className="text-xl font-bold text-white mb-4">TELEGRAM USERS</h2>

        {loading ? (
          <div className="text-center text-gray-400">Loading users...</div>
        ) : users.length === 0 ? (
          <div className="text-center text-gray-400">No users found</div>
        ) : (
          <div className="space-y-3">
            {users.map(user => (
              <div
                key={user.id}
                className="bg-black/30 rounded-lg p-4 flex justify-between items-center"
              >
                <div>
                  <p className="font-medium text-white">
                    {user.username}{" "}
                    <span className="text-xs text-gray-400">({user.role})</span>
                  </p>
                  <p className="text-xs text-gray-400">ID: {user.id}</p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() =>
                      handleRoleChange(
                        user.id,
                        user.username,
                        user.role === "CALLER" ? "SHOT_CALLER" : "CALLER"
                      )
                    }
                    className="text-xs px-2 py-1 bg-blue-600/30 hover:bg-blue-600/50 text-blue-300 rounded whitespace-nowrap block"
                  >
                    {user.role === "CALLER" ? "Make Shot Caller" : "Make Caller"}
                  </button>
                  <button
                    onClick={() => handleDeleteUser(user.id, user.username)}
                    className="text-xs px-2 py-1 bg-red-600/30 hover:bg-red-600/50 text-red-300 rounded whitespace-nowrap block"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      <TelegramUserSearch onUserAdded={loadUsers} />
    </div>
  )
} 