import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps

import bcrypt
from flask import session, redirect, url_for, request, jsonify
from controller import db



def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(64)


#Done
def login_user(email: str, password: str, device_info: str = None, latitude=None, longitude=None):
    user_data = db.get_use_data_by_email(email)
    if not user_data:
        return None, "Invalid email or password."

    # Validate hash format before checking
    stored_hash = user_data["password"].strip()
    if not stored_hash.startswith("$2b$") or len(stored_hash) != 60:
        return None, "Invalid email or password."

    # bcrypt check
    if not bcrypt.checkpw(password.encode("utf-8"), user_data["password"].encode("utf-8")):
        return None, "Invalid email or password."

    # Flask session
    session.permanent = True
    session["user_id"]   = user_data["user_id"]
    session["user_code"] = user_data["user_code"]
    session["user_name"] = user_data["user_name"]
    session["email"]     = user_data["email"]
    session["user_type"] = user_data["user_type"]

    # Create refresh token
    raw_token = generate_refresh_token()
    token_hash = hash_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)

    #create new session in database
    result = db.create_new_session_token(user_id=user_data["user_id"], token_hash=token_hash, device_info=device_info, latitude=latitude, longitude=longitude, expires_at=expires_at)

    if not result:
        return None, "Could not create new session."
    session["refresh_token"] = raw_token
    return user_data, None


def logout_user():
    raw_token = session.get("refresh_token")
    if raw_token:
        token_hash = hash_token(raw_token)
        db.revoked_session_token(token_hash)
    session.clear()


def get_current_user():
    if "user_id" not in session:
        return None
    return {
        "user_id":   session["user_id"],
        "user_code": session["user_code"],
        "user_name": session["user_name"],
        "email":     session["email"],
        "user_type": session["user_type"],
    }


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"error": "Authentication required."}), 401
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated