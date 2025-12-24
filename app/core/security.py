from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.supabase import get_supabase_client

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validates the Bearer token using Supabase Auth.
    Returns the user_id if the token is valid.
    Raises 401 Unauthorized if invalid.
    """
    token = credentials.credentials
    supabase = get_supabase_client()

    try:
        # Verify the session/token with Supabase
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return user_response.user.id

    except Exception as e:
        # Log the error in production
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
