# Telegram User Admin Panel

This is a secure admin panel built with Next.js and Firebase for managing Telegram users in the WAGMI platform.

## Features

- 🔐 Authentication with Firebase Auth
- 🔒 Admin-only access control
- 🔍 Search for Telegram users
- ➕ Add users to Firestore with roles
- 🔄 Change user roles (CALLER/SHOT_CALLER)
- ❌ Remove users
- 📱 Responsive design

## Setup

### 1. Firebase Configuration

Make sure your Firebase project has Authentication enabled:

1. Go to the Firebase Console
2. Select your project
3. Navigate to "Authentication" in the left menu
4. Enable "Email/Password" authentication method
5. Add an admin user through the Firebase console

### 2. Environment Variables

Add these environment variables to your `.env.local` file:

```
# Firebase config
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-messaging-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id

# For the Telegram API (Server only)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

### 3. Admin Configuration

Update the authorized admin emails in `components/admin/admin-layout.tsx`:

```typescript
const ADMIN_EMAILS = [
  "your-admin-email@example.com",
  "another-admin@example.com"
]
```

## Accessing the Admin Panel

The admin panel is available at `/admin` and requires authentication.

1. Navigate to `http://localhost:3000/admin` (or your deployed URL)
2. Log in with your admin email and password
3. If your email matches the authorized admin list, you'll be granted access

## Using the Admin Panel

### Searching for Telegram Users

1. Enter a Telegram username in the search field
2. Click "Search"
3. If found, select a role (CALLER or SHOT_CALLER) and click "Add User"

### Managing Existing Users

1. View all users in the table
2. Change roles by clicking the role toggle button
3. Delete users by clicking the delete button

## Security Notes

- The admin panel implements role-based access control
- Only authorized admin emails can access the panel
- Firebase Authentication provides secure user management
- Telegram API calls are handled server-side to protect tokens

## Implementation Details

- Next.js App Router for routing
- Firebase Authentication for user management
- Firestore for data storage
- Server-side API route for Telegram API integration
- Client-side React components for UI

## Future Enhancements

- Add pagination for larger user lists
- Implement sorting and filtering
- Add activity logging for admin actions
- Support for bulk user operations 