from fastapi import Depends, HTTPException
from ...auth import get_current_user
from ...db.client import supabase, supabase_admin

async def get_db():
    return supabase

async def get_admin_db():
    return supabase_admin
