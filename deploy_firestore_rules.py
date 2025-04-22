import subprocess
import os
import sys
import json

# Path to the service account key
SERVICE_ACCOUNT_PATH = "./wagmi-crypto-calls-firebase-adminsdk-fbsvc-88527b62f1.json"

def main():
    # Check if service account file exists
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        print(f"❌ Service account file not found at {SERVICE_ACCOUNT_PATH}")
        print("Please make sure you have the correct service account key file")
        sys.exit(1)
    
    # Load service account to get project ID
    try:
        with open(SERVICE_ACCOUNT_PATH, 'r') as f:
            service_account = json.load(f)
            project_id = service_account.get('project_id')
            
        if not project_id:
            print("❌ Could not find project_id in service account file")
            sys.exit(1)
            
        print(f"📁 Using Firebase project: {project_id}")
    except Exception as e:
        print(f"❌ Error reading service account file: {e}")
        sys.exit(1)
    
    # Check if firestore.rules exists
    if not os.path.exists("firestore.rules"):
        print("❌ firestore.rules file not found in current directory")
        print("Creating a default rules file that allows access to the roles collection")
        
        with open("firestore.rules", "w") as f:
            f.write("""rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow public read/write access to the roles collection
    // since this is a local admin panel with no authentication
    match /roles/{document=**} {
      allow read, write: if true;
    }
    
    // Default rule - deny all other access
    match /{document=**} {
      allow read, write: if false;
    }
  }
}""")
        print("✅ Created firestore.rules file")
    
    # Create firebase.json if it doesn't exist
    if not os.path.exists("firebase.json"):
        with open("firebase.json", "w") as f:
            f.write(f"""{{
  "firestore": {{
    "rules": "firestore.rules",
    "indexes": "firestore.indexes.json"
  }},
  "project": "{project_id}"
}}""")
        print("✅ Created firebase.json file")
    
    # Create empty firestore.indexes.json if it doesn't exist
    if not os.path.exists("firestore.indexes.json"):
        with open("firestore.indexes.json", "w") as f:
            f.write("""{"indexes":[],"fieldOverrides":[]}""")
        print("✅ Created empty firestore.indexes.json file")
    
    print("\n🔥 Deploying Firestore rules...")
    
    try:
        # Check if Firebase CLI is installed
        subprocess.run(["firebase", "--version"], check=True, capture_output=True)
        
        # Deploy the rules
        result = subprocess.run(
            ["firebase", "deploy", "--only", "firestore:rules", "--project", project_id],
            check=True,
            capture_output=True,
            text=True
        )
        
        print("\n✅ Successfully deployed Firestore rules!")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error deploying Firestore rules: {e}")
        print("\nOutput:")
        print(e.stdout if hasattr(e, 'stdout') else "")
        print("\nError:")
        print(e.stderr if hasattr(e, 'stderr') else "")
        
        print("\n🔧 You may need to install the Firebase CLI and login:")
        print("1. npm install -g firebase-tools")
        print("2. firebase login")
        print(f"3. firebase deploy --only firestore:rules --project {project_id}")
        
    except FileNotFoundError:
        print("\n❌ Firebase CLI not found")
        print("\n🔧 Please install the Firebase CLI first:")
        print("npm install -g firebase-tools")
        print("firebase login")
        print(f"firebase deploy --only firestore:rules --project {project_id}")

if __name__ == "__main__":
    main() 