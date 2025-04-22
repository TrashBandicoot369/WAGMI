"use client"

import { useState, useEffect } from "react"
import { useAuth } from "@/lib/auth-context"
import { LoginForm } from "./login-form"
import { useRouter } from "next/navigation"

// Update this list with your admin email(s)
const ADMIN_EMAILS = [
  "admin@example.com",
  "mitchsweeney@gmail.com",
  // Add your email here, for example:
  // "youremail@example.com",
  // IMPORTANT: Make sure to add your actual email address here
  "*", // Temporarily allow any email for testing
]

export function AdminLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, signOut } = useAuth()
  const [authorized, setAuthorized] = useState(false)
  const router = useRouter()

  useEffect(() => {
    // Check if the current user is an authorized admin
    if (!loading) {
      console.log("Auth state:", { user: user?.email || "No user", loading })
      
      if (user) {
        // Temporarily authorize any logged-in user for testing
        const isAdmin = ADMIN_EMAILS.includes("*") || ADMIN_EMAILS.includes(user.email || "")
        console.log("Authorization check:", { email: user.email, isAdmin })
        setAuthorized(isAdmin)
        
        if (!isAdmin) {
          // If not authorized, sign out
          console.log("User not authorized, signing out")
          signOut()
        }
      }
    }
  }, [user, loading, signOut])

  const handleSignOut = async () => {
    await signOut()
    router.push("/")
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 to-black p-4">
        <div className="animate-pulse text-white text-xl">Loading...</div>
      </div>
    )
  }

  if (!user || !authorized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 to-black p-4">
        <LoginForm />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black">
      <header className="sticky top-0 z-50 bg-black/30 backdrop-blur-lg border-b border-white/10">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-white">WAGMI Admin</h1>
            <span className="bg-green-500/20 text-green-400 px-2 py-0.5 rounded text-xs">
              {user.email}
            </span>
          </div>
          
          <button
            onClick={handleSignOut}
            className="px-3 py-1 bg-red-600/20 hover:bg-red-600/40 text-red-300 rounded transition-colors text-sm"
          >
            Sign Out
          </button>
        </div>
      </header>
      
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  )
} 