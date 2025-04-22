"use client"

import { useEffect, useState } from "react"
import { db } from "@/lib/firebase-client"
import {
  collection,
  getDocs,
  setDoc,
  doc,
  deleteDoc,
  serverTimestamp
} from "firebase/firestore"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

type Role = "CALLER" | "SHOT_CALLER"

interface User {
  id: string
  name: string
  role: Role
}

export default function AdminPage() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [lookupLoading, setLookupLoading] = useState(false)
  const [formData, setFormData] = useState({
    id: "",
    username: "",
    name: "",
    role: "CALLER" as Role
  })

  const fetchUsers = async () => {
    setLoading(true)
    try {
      const rolesCollection = collection(db, "roles")
      const snapshot = await getDocs(rolesCollection)

      const fetchedUsers: User[] = []
      snapshot.forEach((doc) => {
        const data = doc.data()
        fetchedUsers.push({
          id: doc.id,
          name: data.name,
          role: data.role as Role
        })
      })

      setUsers(fetchedUsers)
    } catch (error) {
      console.error("Error fetching users:", error)
    } finally {
      setLoading(false)
    }
  }

  const lookupTelegramId = async (username: string) => {
    if (!username) {
      alert("Please enter a Telegram username")
      return
    }

    setLookupLoading(true)
    try {
      const cleanUsername = username.startsWith('@')
        ? username.substring(1).toLowerCase()
        : username.toLowerCase()

      // Use the API endpoint to lookup the user ID
      const response = await fetch('/api/telegram/lookup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: cleanUsername }),
      })

      const data = await response.json()
      
      if (response.ok && data.userId) {
        setFormData({
          ...formData,
          id: data.userId.toString(),
          name: cleanUsername,
        })
        return
      } 
      
      // If we get here, there was an error or the user wasn't found
      if (data.error) {
        throw new Error(data.error)
      } else {
        throw new Error("User not found")
      }
    } catch (error) {
      console.error("API lookup failed:", error)
      const errorMessage = error instanceof Error ? error.message : 'Failed to look up ID'
      
      // Show more helpful error message directing user to run the Python script
      alert(`${errorMessage}\n\nPlease run the get_user_ids.py script with this username and enter the ID manually.`)
      
      // Still set the name in the form
      setFormData({ ...formData, name: username.replace('@', '') })
    } finally {
      setLookupLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.id || !formData.name) return alert("Fill all fields")
    await saveUser({ id: formData.id, name: formData.name, role: formData.role })
    setFormData({ id: "", username: "", name: "", role: "CALLER" })
  }

  const saveUser = async (user: User) => {
    try {
      const roleData = {
        name: user.name,
        role: user.role,
        createdAt: serverTimestamp(),
        addedBy: "admin-panel"
      }

      const telegramUserData = {
        username: user.name.toLowerCase(),
        role: user.role,
        addedAt: serverTimestamp(),
        addedBy: "admin-panel"
      }

      await setDoc(doc(db, "roles", user.id), roleData)
      await setDoc(doc(db, "telegramUsers", user.id), telegramUserData)

      fetchUsers()
    } catch (error) {
      console.error("Error saving user:", error)
    }
  }

  const handleRemoveUser = async (userId: string) => {
    try {
      await deleteDoc(doc(db, "roles", userId))
      await deleteDoc(doc(db, "telegramUsers", userId))
      fetchUsers()
    } catch (error) {
      console.error("Error removing user:", error)
      alert("Failed to remove user")
    }
  }

  const handleToggleRole = async (user: User) => {
    const newRole: Role = user.role === "CALLER" ? "SHOT_CALLER" : "CALLER"
    try {
      await setDoc(doc(db, "roles", user.id), {
        name: user.name,
        role: newRole,
        updatedAt: serverTimestamp(),
      }, { merge: true })

      await setDoc(doc(db, "telegramUsers", user.id), {
        username: user.name.toLowerCase(),
        role: newRole,
        updatedAt: serverTimestamp(),
      }, { merge: true })

      fetchUsers()
    } catch (error) {
      console.error("Error updating role:", error)
      alert("Failed to update role")
    }
  }

  useEffect(() => {
    fetchUsers()
  }, [])

  useEffect(() => {
    if (formData.username && !formData.name) {
      const cleanUsername = formData.username.startsWith('@')
        ? formData.username.substring(1)
        : formData.username
      setFormData(prev => ({ ...prev, name: cleanUsername }))
    }
  }, [formData.username])

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <h1 className="text-3xl font-bold mb-6">WAGMI Admin Panel</h1>

      <Card className="p-6 mb-8 bg-gray-800 border-gray-700">
        <h2 className="text-xl font-semibold mb-4">Add New User</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Telegram Username</Label>
              <Input
                placeholder="e.g. username or @username"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              />
            </div>
            <div className="flex items-end">
              <Button
                type="button"
                onClick={() => lookupTelegramId(formData.username)}
                disabled={lookupLoading || !formData.username}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {lookupLoading ? "Looking up..." : "Look up ID"}
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Telegram ID</Label>
              <Input
                placeholder="e.g. 12345678"
                value={formData.id}
                onChange={(e) => setFormData({ ...formData, id: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label>Display Name</Label>
              <Input
                placeholder="Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label>Role</Label>
              <Select
                value={formData.role}
                onValueChange={(value: Role) => setFormData({ ...formData, role: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="CALLER">CALLER</SelectItem>
                  <SelectItem value="SHOT_CALLER">SHOT_CALLER</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <Button type="submit">Add User</Button>
        </form>
      </Card>

      <Card className="p-6 bg-gray-800 border-gray-700">
        <h2 className="text-xl font-semibold mb-4">Current Users</h2>
        {loading ? (
          <p>Loading users...</p>
        ) : users.length === 0 ? (
          <p>No users found.</p>
        ) : (
          <div className="space-y-2">
            {users.map((user) => (
              <div
                key={user.id}
                className="flex justify-between items-center bg-gray-900 px-4 py-2 rounded-md"
              >
                <div>
                  <p className="font-medium text-white">
                    {user.name}{" "}
                    <span className="text-gray-400 text-sm">({user.role})</span>
                  </p>
                  <p className="text-sm text-gray-400">{user.id}</p>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    onClick={() => handleToggleRole(user)}
                    className={user.role === "CALLER" 
                      ? "bg-blue-600 hover:bg-blue-700 text-white text-xs px-3 py-1" 
                      : "bg-purple-600 hover:bg-purple-700 text-white text-xs px-3 py-1"}
                  >
                    {user.role === "CALLER" ? "Promote" : "Demote"}
                  </Button>
                  <Button
                    onClick={() => handleRemoveUser(user.id)}
                    className="bg-red-600 hover:bg-red-700 text-white text-xs px-3 py-1"
                  >
                    Remove
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}
