import base64
import secrets
import uuid
from io import BytesIO
from typing import List, Literal

import boto3
import pymupdf
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PIL import Image, ImageFilter
from pydantic import BaseModel

from app.auth import get_current_user

from ....config import settings
from ....db.client import supabase_admin

s3 = boto3.client(
    service_name="s3",
    endpoint_url=settings.S3_ENDPOINT_URL,
    aws_access_key_id=settings.S3_ACCESS_KEY_ID,
    aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
    region_name="auto",
)

router = APIRouter()


class GetFiles(BaseModel):
    filter: Literal["private", "shared"]


@router.post("/")
async def get_user_files(req: GetFiles, userid=Depends(get_current_user)):
    class File(BaseModel):
        fileId: str
        fileName: str
        previewImage: str

    data = None
    files: List[File] = []
    # Get files based on filter
    if req.filter == "private":
        # Get only owned files
        data = supabase_admin.table("files").select("*").eq("owner", userid).execute()
    else:
        data = (
            supabase_admin.table("files")
            .select("id, filename, preview_image, shared!inner(shared_with)")
            .eq("shared.shared_with", userid)
            .execute()
        )

    if data.data is not None:
        for db_file in data.data:
            file = File(
                fileId=db_file["id"],
                fileName=db_file["filename"],
                previewImage=db_file["preview_image"],
            )
            files.append(file)

    return {"message": "Files retrieved successfully", "files": files}


def squarify_image(image: Image.Image, size: int = 256) -> Image.Image:
    # Create a square canvas with blurred background
    target_size = (size, size)
    result = Image.new("RGBA", target_size, (255, 255, 255, 0))

    # Create blurred background from original
    background = image.copy()
    background = background.resize(target_size, Image.Resampling.BILINEAR)
    background = background.filter(ImageFilter.GaussianBlur(radius=10))

    # Resize original image maintaining aspect ratio
    aspect = image.width / image.height
    if aspect > 1:
        new_width = size
        new_height = int(size / aspect)
    else:
        new_width = int(size * aspect)
        new_height = size

    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Calculate position to center the image
    x = (size - new_width) // 2
    y = (size - new_height) // 2

    # Paste background first, then the resized image
    result.paste(background, (0, 0))
    result.paste(image, (x, y))

    return result


def generate_preview_image(file_content: bytes, filename: str) -> str:
    print(filename)
    # Check if the file is in the supported formats
    if filename.lower().endswith((".png", ".jpeg", ".jpg")):
        # Open the image file from bytes
        image = Image.open(BytesIO(file_content))

        # Create squared thumbnail with blur background
        squared_image = squarify_image(image)

        # Convert the thumbnail to PNG format and save to a BytesIO object
        preview_image = BytesIO()
        squared_image.save(preview_image, format="PNG")

        # Encode the image to base64
        preview_image_base64 = base64.b64encode(preview_image.getvalue()).decode(
            "utf-8"
        )
        return preview_image_base64

    elif filename.lower().endswith(".pdf"):
        print("PDF")
        # Open the PDF file from bytes
        pdf_document = pymupdf.open(stream=file_content, filetype="pdf")
        # Get the first page
        page = pdf_document[0]
        # Render page to pixmap with reasonable resolution
        pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))  # type: ignore
        # Convert pixmap to PIL Image
        pngtobytes = pix.tobytes("png")
        image = Image.open(BytesIO(pngtobytes))

        # Create squared thumbnail with blur background
        squared_image = squarify_image(image)

        # Convert the thumbnail to PNG format and save to a BytesIO object
        preview_image = BytesIO()
        squared_image.save(preview_image, format="PNG")

        # Encode the image to base64
        preview_image_base64 = base64.b64encode(preview_image.getvalue()).decode(
            "utf-8"
        )
        return preview_image_base64
    else:
        raise ValueError(
            "Unsupported file format. Only PDF, PNG, JPEG, and JPG are supported."
        )


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), userid=Depends(get_current_user)):
    if file.filename is None:
        raise HTTPException(status_code=400, detail="File name is required")
    try:
        file_content = await file.read()
        file_key = secrets.token_urlsafe(32)
        s3.upload_fileobj(BytesIO(file_content), "skydrive", file_key)
        id = str(uuid.uuid4())
        file_data = {
            "id": id,
            "file_url": f"https://dl-skydrive.akshatsaraswat.in/{file_key}",
            "owner": userid,
            "preview_image": generate_preview_image(file_content, file.filename),
            "filename": file.filename,
        }
        supabase_admin.table("files").insert(file_data).execute()

        return {
            "message": "File uploaded successfully",
            "fileId": id,
            "fileName": file.filename,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{fileId}/preview")
async def preview_file(fileId: str, userid=Depends(get_current_user)):
    # Get file data
    file = supabase_admin.table("files").select("*").eq("id", fileId).execute()
    if not file.data:
        raise HTTPException(status_code=404, detail="File not found")

    file_data = file.data[0]

    # Check if user has access (either owner or shared)
    shared_access = (
        supabase_admin.table("shared")
        .select("*")
        .eq("file_id", fileId)
        .eq("shared_with", userid)
        .execute()
    )
    if file_data["owner"] != userid and not shared_access.data:
        raise HTTPException(status_code=403, detail="Access denied")
    shared_emails = []

    if file_data["is_shared"]:
        # get shared users of the file
        shared_users_query = (
            supabase_admin.table("shared")
            .select("shared_with")
            .eq("file_id", fileId)
            .execute()
        )
        shared_users = [
            user["shared_with"]
            for user in shared_users_query.data
            if user["shared_with"]
        ]
        shared_emails = map(
            lambda user_id: supabase_admin.auth.admin.get_user_by_id(
                user_id
            ).user.email,
            shared_users,
        )

    # Get owner email
    owner_data = supabase_admin.auth.admin.get_user_by_id(file_data["owner"]).user
    owner_email = owner_data.email if owner_data else "unknown"

    return {
        "message": "File preview retrieved successfully",
        "fileId": file_data["id"],
        "fileName": file_data["filename"],
        "downloadURL": file_data["file_url"],
        "previewImage": file_data["preview_image"],
        "createdAt": file_data["created_at"],
        "createdBy": owner_email,
        "isShared": file_data["is_shared"],
        "sharedWith": list(shared_emails),
    }


class ShareReqBody(BaseModel):
    email: str


@router.patch("/{fileId}/share")
async def share_file(fileId: str, req: ShareReqBody, userid=Depends(get_current_user)):
    try:
        print(fileId)
        # Check file ownership
        file_query = (
            supabase_admin.table("files").select("owner").eq("id", fileId).execute()
        )
        if not file_query.data:
            return {"message": "File not found"}

        if file_query.data[0]["owner"] != userid:
            return {"message": "You are not the owner of this file"}

        # Get recipient ID
        recipient_query = supabase_admin.rpc(
            "get_user_id_by_email", {"email": req.email}
        ).execute()
        if not recipient_query.data:
            return {"message": "Recipient not found"}

        recipient_id = recipient_query.data[0]["id"]

        # Check if file is already shared with this user
        existing_share = (
            supabase_admin.table("shared")
            .select("*")
            .eq("file_id", fileId)
            .eq("shared_with", recipient_id)
            .execute()
        )

        if existing_share.data:
            return {"message": "File is already shared with this user"}

        # Update file and create sharing record
        supabase_admin.table("files").update({"is_shared": True}).eq(
            "id", fileId
        ).execute()
        supabase_admin.table("shared").insert(
            {"file_id": fileId, "shared_with": recipient_id}
        ).execute()

        return {"message": "File shared successfully"}
    except Exception as e:
        return {"message": str(e)}


@router.delete("/{fileId}")
async def delete_file(fileId: str, userid=Depends(get_current_user)):
    file = (
        supabase_admin.table("files")
        .select("owner, file_url")
        .eq("id", fileId)
        .execute()
    )
    if not file.data:
        raise HTTPException(status_code=404, detail="File not found")
    if file.data[0]["owner"] != userid:
        raise HTTPException(
            status_code=403, detail="You are not the owner of this file"
        )
    print(file)
    s3.delete_object(Bucket="skydrive", Key=file.data[0]["file_url"].split("/")[-1])
    supabase_admin.table("files").delete().eq("id", fileId).execute()
    return {"message": "File deleted successfully"}


class SearchReqBody(BaseModel):
    query: str


@router.post("/search")
async def search_files(req: SearchReqBody, userid=Depends(get_current_user)):
    class File(BaseModel):
        fileId: str
        fileName: str
        previewImage: str

    # Query for owned and shared files using PostgreSQL RPC
    data = supabase_admin.rpc(
        "search_files", {"search_query": req.query.lower(), "user_id": userid}
    ).execute()

    files: List[File] = []

    if data.data is not None:
        for db_file in data.data:
            file = File(
                fileId=db_file["id"],
                fileName=db_file["filename"],
                previewImage=db_file["preview_image"],
            )
            files.append(file)

    return {"message": "Files retrieved successfully", "files": files}
