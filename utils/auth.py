"""
Firebase Authentication with OTP Login
Handles user authentication and session management
"""

import pyrebase
import os
from typing import Optional, Dict
import json

# Firebase configuration
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyB_Q6cnfqV4Gf80t8nIxv0o7fvzzuA5Tkc",
    "authDomain": "ai-project-49a92.firebaseapp.com",
    "projectId": "ai-project-49a92",
    "storageBucket": "ai-project-49a92.firebasestorage.app",
    "messagingSenderId": "964094089317",
    "appId": "1:964094089317:web:011c283adc350de7b68e8c",
    "measurementId": "G-54GDRXYFW4",
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL", "https://ai-project-49a92-default-rtdb.firebaseio.com/")
}

# Initialize Firebase
firebase = None
auth = None
db = None

try:
    # Initialize Firebase with the provided config
    firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
    auth = firebase.auth()
    
    # Try to initialize database (may fail if Realtime DB not set up yet)
    try:
        db = firebase.database()
        print("[OK] Firebase initialized successfully (with database)")
    except Exception as db_error:
        print(f"[INFO] Firebase initialized (database not available yet: {db_error})")
        db = None
    
    print("[OK] Firebase authentication ready")
except Exception as e:
    print(f"[WARNING] Firebase initialization failed: {e}")
    print("[INFO] App will run in guest mode without authentication")
    print("[TIP] Make sure pyrebase4 is installed: pip install pyrebase4")

def send_otp(phone_number: str) -> Dict:
    """Send OTP to phone number."""
    if not auth:
        return {"success": False, "error": "Firebase not configured"}
    
    try:
        # Firebase Phone Auth requires setup in Firebase Console
        # This is a placeholder - actual implementation needs Firebase project setup
        verification_id = auth.send_verification_code(phone_number)
        return {"success": True, "verification_id": verification_id}
    except Exception as e:
        return {"success": False, "error": str(e)}

def verify_otp(verification_id: str, otp: str) -> Dict:
    """Verify OTP and login user."""
    if not auth:
        return {"success": False, "error": "Firebase not configured"}
    
    try:
        # Verify OTP
        user = auth.sign_in_with_verification_code(verification_id, otp)
        return {"success": True, "user": user}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_current_user() -> Optional[Dict]:
    """Get currently logged in user."""
    if not auth:
        return None
    
    try:
        # This would typically come from session/token
        # Placeholder implementation
        return None
    except:
        return None

def save_chat_history(user_id: str, chat_history: list):
    """Save chat history for user."""
    if not firebase or not db:
        # Fallback to local storage
        try:
            os.makedirs("chat_history", exist_ok=True)
            with open(f"chat_history/chats_{user_id}.json", "w", encoding="utf-8") as f:
                json.dump(chat_history, f, ensure_ascii=False, indent=2)
            print(f"[INFO] Chat saved locally for user: {user_id}")
        except Exception as e:
            print(f"[WARNING] Failed to save chat locally: {e}")
        return
    
    try:
        db.child("users").child(user_id).child("chats").set(chat_history)
        print(f"[OK] Chat saved to Firebase for user: {user_id}")
    except Exception as e:
        print(f"[WARNING] Failed to save chat to Firebase: {e}")
        # Fallback to local
        try:
            os.makedirs("chat_history", exist_ok=True)
            with open(f"chat_history/chats_{user_id}.json", "w", encoding="utf-8") as f:
                json.dump(chat_history, f, ensure_ascii=False, indent=2)
            print(f"[INFO] Chat saved locally as fallback")
        except:
            pass

def load_chat_history(user_id: str) -> list:
    """Load chat history for user."""
    # Try Firebase first if available
    if firebase and db:
        try:
            chats = db.child("users").child(user_id).child("chats").get()
            if chats.val():
                print(f"[OK] Loaded chat from Firebase for user: {user_id}")
                return chats.val()
        except Exception as e:
            print(f"[INFO] Could not load from Firebase: {e}")
    
    # Fallback to local storage
    try:
        with open(f"chat_history/chats_{user_id}.json", "r", encoding="utf-8") as f:
            print(f"[INFO] Loaded chat from local storage for user: {user_id}")
            return json.load(f)
    except FileNotFoundError:
        # No chat history exists yet
        return []
    except Exception as e:
        print(f"[WARNING] Failed to load chat: {e}")
        return []

