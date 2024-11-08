### 1. Create an Account

**Route:** `/api/auth/signup`  
**Method:** `POST`

#### Request Body

```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

#### Response

- **201 Created**: Account successfully created.
- **400 Bad Request**: Invalid input data.
- **409 Conflict**: Email or username already exists.

```json
{
  "message": "Account created successfully",
  "userId": "string"
}
```

---

### 2. Sign In

**Route:** `/api/auth/signin`  
**Method:** `POST`

#### Request Body

```json
{
  "email": "string",
  "password": "string"
}
```

#### Response

- **200 OK**: Successful login.
- **401 Unauthorized**: Invalid email or password.

```json
{
  "message": "Login successful",
  "token": "string",
  "userId": "string",
  "username": "string"
}
```

---

### 3. Get User Files

**Route:** `/api/files`  
**Method:** `POST`

#### Request Body

```json
{
  "filter": "shared" | "private" | "public",
}
```

#### Response

- **200 OK**: Returns a paginated list of files.
- **401 Unauthorized**: User is not authenticated.

```json
{
  "message": "Files retrieved successfully",
  "files": [
    {
      "fileId": "string",
      "fileName": "string",
      "previewImage": "base64png"
    }
  ]
}
```

---

### 4. Upload a File

**Route:** `/api/files/upload`  
**Method:** `POST`  
**Headers:**

- `Content-Type: multipart/form-data`

#### Request Body (Form Data)

- `file` - File to be uploaded (binary data)
- `isPublic` (optional) - Boolean indicating if the file should be public (default is `false`).

#### Response

- **201 Created**: File successfully uploaded.
- **400 Bad Request**: File upload failed.
- **401 Unauthorized**: User is not authenticated.

```json
{
  "message": "File uploaded successfully",
  "fileId": "string",
  "fileName": "string"
}
```

---

### 5. Preview a File

**Route:** `/api/files/{fileId}/preview`  
**Method:** `GET`

#### Path Parameters

- `fileId` (string) - ID of the file to preview.

#### Response

- **200 OK**: Returns file preview information (e.g., URL or file data).
- **401 Unauthorized**: User is not authenticated.
- **404 Not Found**: File does not exist or access is restricted.

```json
{
  "message": "File preview retrieved successfully",
  "fileId": "string",
  "downloadURL": "string",
  "previewImage": "base64png",
  "createdAt": "string",
  "createdBy": "string",
  "isShared": "boolean",
  "sharedWith": ["string"]
}
```

---

### 7. Change Sharing Options (Public/Private)

**Route:** `/api/files/{fileId}/share`  
**Method:** `PATCH`

#### Path Parameters

- `fileId` (string) - ID of the file to update sharing options.

#### Request Body

```json
{
  "email": "string"
}
```

#### Response

- **200 OK**: Sharing settings updated successfully.
- **400 Bad Request**: Invalid input data.
- **401 Unauthorized**: User is not authenticated.
- **404 Not Found**: File does not exist.

```json
{
  "message": "Sharing settings updated successfully"
}
```

---

### 8. Delete a File

**Route:** `/api/files/{fileId}`
**Method:** `DELETE`

### Response

- **204 No Content**: File deleted successfully.

```json
{
  "message": "File deleted successfully"
}
```

---

### 9. Search for Files

**Route:** `/api/files/search`
**Method:** `POST`

#### Request Body

```json
{
  "query": "string"
}
```

#### Response

- **200 OK**: Returns a list of files matching the search query.

```json
{
  "message": "Files retrieved successfully",
  "files": [
    {
      "fileId": "string",
      "fileName": "string",
      "previewImage": "base64png"
    }
  ]
}
```
