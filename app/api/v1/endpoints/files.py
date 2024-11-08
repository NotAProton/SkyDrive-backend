import boto3
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
from ....db.client import supabase
from ....config import settings


s3 = boto3.client(
    service_name="s3",
    endpoint_url=settings.S3_ENDPOINT_URL,
    aws_access_key_id=settings.S3_ACCESS_KEY_ID,
    aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
    region_name="auto",
)

router = APIRouter()

@router.post("/")
async def get_user_files(filter: str):
    files = supabase.table('files').select('*').eq('filter', filter).execute()
    return {
        "message": "Files retrieved successfully",
        "files": files.data
    }

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        s3.upload_fileobj(file.file, 'bucket_name', file.filename)
        file_data = {
            "fileId": "generated_file_id",
            "fileName": file.filename,
            "previewImage": "base64_encoded_image"
        }
        supabase.table('files').insert(file_data).execute()
        return {
            "message": "File uploaded successfully",
            "fileId": file_data["fileId"],
            "fileName": file_data["fileName"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{fileId}/preview")
async def preview_file(fileId: str):
    file = supabase.table('files').select('*').eq('fileId', fileId).execute()
    if not file.data:
        raise HTTPException(status_code=404, detail="File not found")
    return {
        "message": "File preview retrieved successfully",
        "fileId": file.data[0]["fileId"],
        "downloadURL": "generated_download_url",
        "previewImage": file.data[0]["previewImage"],
        "createdAt": file.data[0]["createdAt"],
        "createdBy": file.data[0]["createdBy"],
        "isShared": file.data[0]["isShared"],
        "sharedWith": file.data[0]["sharedWith"]
    }

@router.patch("/{fileId}/share")
async def share_file(fileId: str, email: str):
    file = supabase.table('files').select('*').eq('fileId', fileId).execute()
    if not file.data:
        raise HTTPException(status_code=404, detail="File not found")
    shared_with = file.data[0].get("sharedWith", [])
    shared_with.append(email)
    supabase.table('files').update({"sharedWith": shared_with}).eq('fileId', fileId).execute()
    return {
        "message": "Sharing settings updated successfully"
    }

@router.delete("/{fileId}")
async def delete_file(fileId: str):
    file = supabase.table('files').select('*').eq('fileId', fileId).execute()
    if not file.data:
        raise HTTPException(status_code=404, detail="File not found")
    supabase.table('files').delete().eq('fileId', fileId).execute()
    return {
        "message": "File deleted successfully"
    }

@router.post("/search")
async def search_files(query: str):
    files = supabase.table('files').select('*').ilike('fileName', f'%{query}%').execute()
    return {
        "message": "Files retrieved successfully",
        "files": files.data
    }

