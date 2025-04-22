import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
try:
    # Use the service account key file
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    
    # Initialize Firestore client
    db = firestore.client()
    print("✅ Firebase Admin SDK initialized successfully")
except Exception as e:
    print(f"❌ Error initializing Firebase Admin: {e}")
    # Still provide a db object to avoid breaking imports, but operations will fail
    db = None 