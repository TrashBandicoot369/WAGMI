import firebase_admin
from firebase_admin import credentials, firestore

# Make sure the path to your service account JSON is correct
cred = credentials.Certificate("wagmi-crypto-calls-firebase-adminsdk-fbsvc-88527b62f1.json")

# Avoid reinitializing if already initialized
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client() 