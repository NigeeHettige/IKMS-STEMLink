"""functions for creating database instances."""

from ..config import get_settings

from supabase import create_client


def get_supabase_client():

    settings = get_settings()

    return create_client(settings.supabase_url, settings.supabase_key),settings.bucket_name
    
  
