from supabase import create_client
from ..config import settings

supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_KEY
)

# For admin operations (like user management)
supabase_admin = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SECRET_KEY
)
