"""
Authentication and Authorization Module
JWT-based authentication with role-based access control
"""

import hashlib
import os
import secrets
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Optional

import jwt
from flask import jsonify, request

# JWT Configuration
JWT_SECRET = os.environ.get("JWT_SECRET", secrets.token_hex(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# User database (in production, use proper DB)
USERS_DB = {
    "admin": {
        "id": 1,
        "username": "admin",
        "password_hash": hashlib.sha256(
            b"admin123"
        ).hexdigest(),  # Change in production!
        "role": "admin",
        "created_at": datetime.now().isoformat(),
    }
}


class AuthManager:
    """Handle authentication and authorization"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return AuthManager.hash_password(password) == password_hash

    @staticmethod
    def create_token(user_id: int, username: str, role: str) -> str:
        """Create JWT token"""
        payload = {
            "user_id": user_id,
            "username": username,
            "role": role,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> Optional[Dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def authenticate(username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return token"""
        user = USERS_DB.get(username)
        if not user:
            return None

        if not AuthManager.verify_password(password, user["password_hash"]):
            return None

        token = AuthManager.create_token(user["id"], user["username"], user["role"])
        return {"token": token, "user": {"username": username, "role": user["role"]}}

    @staticmethod
    def create_user(username: str, password: str, role: str = "user") -> Optional[int]:
        """Create new user"""
        if username in USERS_DB:
            return None

        user_id = len(USERS_DB) + 1
        USERS_DB[username] = {
            "id": user_id,
            "username": username,
            "password_hash": AuthManager.hash_password(password),
            "role": role,
            "created_at": datetime.now().isoformat(),
        }
        return user_id

    @staticmethod
    def get_user(username: str) -> Optional[Dict]:
        """Get user by username"""
        user = USERS_DB.get(username)
        if user:
            return {
                "id": user["id"],
                "username": user["username"],
                "role": user["role"],
                "created_at": user["created_at"],
            }
        return None


def token_required(f):
    """Decorator to require valid JWT token"""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check Authorization header
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        payload = AuthManager.verify_token(token)
        if not payload:
            return jsonify({"error": "Token is invalid or expired"}), 401

        # Add user info to request context
        request.current_user = payload

        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    """Decorator to require admin role"""

    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(request, "current_user"):
            return jsonify({"error": "Authentication required"}), 401

        if request.current_user.get("role") != "admin":
            return jsonify({"error": "Admin privileges required"}), 403

        return f(*args, **kwargs)

    return decorated


# Auth routes
def register_auth_routes(app):
    """Register authentication routes"""

    @app.route("/api/auth/login", methods=["POST"])
    def login():
        data = request.json or {}
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        result = AuthManager.authenticate(username, password)
        if not result:
            return jsonify({"error": "Invalid credentials"}), 401

        return jsonify(result)

    @app.route("/api/auth/register", methods=["POST"])
    def register():
        data = request.json or {}
        username = data.get("username")
        password = data.get("password")
        role = data.get("role", "user")

        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        # Only admin can create admin users
        if role == "admin":
            # Check if request has admin token
            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            payload = AuthManager.verify_token(token)
            if not payload or payload.get("role") != "admin":
                role = "user"  # Downgrade to user

        user_id = AuthManager.create_user(username, password, role)
        if not user_id:
            return jsonify({"error": "Username already exists"}), 409

        return jsonify({"message": "User created", "user_id": user_id})

    @app.route("/api/auth/verify", methods=["GET"])
    @token_required
    def verify():
        return jsonify({"valid": True, "user": request.current_user})

    @app.route("/api/auth/users", methods=["GET"])
    @token_required
    @admin_required
    def list_users():
        users = [
            {
                "id": u["id"],
                "username": u["username"],
                "role": u["role"],
                "created_at": u["created_at"],
            }
            for u in USERS_DB.values()
        ]
        return jsonify({"users": users})
