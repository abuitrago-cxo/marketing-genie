"""
Firebase Authentication Module

This module provides authentication utilities for Firebase in the FastAPI backend.
It includes middleware for verifying Firebase ID tokens and extracting user information.
"""
import os
import json
from typing import Optional, Dict, Any

import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin.auth import ExpiredIdTokenError, RevokedIdTokenError, CertificateFetchError
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK with credentials from environment variables."""
    # Check if Firebase app is already initialized
    if not firebase_admin._apps:
        # Get Firebase service account key from environment variable
        firebase_creds = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
        
        if not firebase_creds:
            raise ValueError(
                "FIREBASE_SERVICE_ACCOUNT_JSON environment variable not set. "
                "Please set it with your Firebase service account JSON."
            )
        
        try:
            # Parse the service account key JSON string
            creds_dict = json.loads(firebase_creds)
            cred = credentials.Certificate(creds_dict)
            
            # Initialize the Firebase Admin SDK
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized successfully")
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON in FIREBASE_SERVICE_ACCOUNT_JSON") from e
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Firebase Admin SDK: {str(e)}") from e

# Call the initialization function when the module is imported
initialize_firebase()

class FirebaseAuthMiddleware(HTTPBearer):
    """Middleware for Firebase Authentication.
    
    This middleware verifies the Firebase ID token in the Authorization header
    and adds the decoded token to the request state.
    """
    
    async def __call__(self, request: Request) -> Optional[Dict[str, Any]]:
        """Verify the Firebase ID token in the Authorization header."""
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header is missing",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme. Use 'Bearer' token",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        token = credentials.credentials
        
        try:
            # Verify the ID token
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except ValueError as e:
            # Invalid token format
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e
        except ExpiredIdTokenError as e:
            # Token has expired
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e
        except RevokedIdTokenError as e:
            # Token has been revoked
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e
        except (CertificateFetchError, auth.AuthError) as e:
            # Error fetching public keys or other auth errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error verifying authentication token",
            ) from e

def get_current_user(token: Dict[str, Any] = Depends(FirebaseAuthMiddleware())) -> Dict[str, Any]:
    """Dependency to get the current authenticated user from the token.
    
    This can be used in FastAPI route dependencies to require authentication.
    """
    return token

def get_current_user_optional(token: Optional[Dict[str, Any]] = Depends(FirebaseAuthMiddleware(auto_error=False))) -> Optional[Dict[str, Any]]:
    """Dependency to optionally get the current authenticated user.
    
    Returns None if no valid token is provided.
    """
    return token if token else None
