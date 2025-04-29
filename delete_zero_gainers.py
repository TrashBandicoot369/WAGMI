import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin_setup import initialize_app

# Initialize Firebase app
initialize_app()
db = firestore.client()

calls_ref = db.collection('calls')
docs = calls_ref.stream()

deleted = 0
for doc in docs:
    data = doc.to_dict()
    try:
        initial = float(data.get('initialMarketCap', 0))
        ath = float(data.get('athMarketCap', 0))
    except Exception:
        continue
    if not initial or not ath or initial <= 0 or ath <= 0:
        continue
    gain = round(((ath - initial) / initial) * 100)
    if gain <= 0:
        print(f"Deleting {doc.id}: gain={gain}")
        doc.reference.delete()
        deleted += 1
print(f"Deleted {deleted} docs with gain <= 0.") 