from supabase import create_client, Client
from app.core.config import settings

def get_supabase_client() -> Client:
    """
    Initializes and returns a Supabase client using the Service Role Key.
    This client has admin privileges and should be used with caution.
    """
    supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    return supabase
