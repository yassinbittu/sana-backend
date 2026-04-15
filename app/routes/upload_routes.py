from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required
from app.middleware.auth_middleware import admin_required
from app.utils.helpers import success_response, error_response, save_uploaded_file, delete_file

upload_bp = Blueprint("upload", __name__)


@upload_bp.post("/image")
@admin_required
def upload_image():
    """
    Upload a product image
    ---
    tags:
      - Upload
    security:
      - Bearer: []
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: Image file to upload
      - in: query
        name: folder
        type: string
        enum: ["products", "misc"]
        example: "products"
    responses:
      201:
        description: Image uploaded successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Image uploaded successfully"
            data:
              type: object
              properties:
                url:
                  type: string
                  example: "/uploads/products/uuid.jpg"
      400:
        description: Bad request
      401:
        description: Unauthorized
    """
    file = request.files.get("file")
    if not file or not file.filename:
        return error_response("No file provided. Use field name 'file'")

    folder = request.args.get("folder", "products")
    # Whitelist allowed folders
    if folder not in ("products", "misc"):
        folder = "products"

    url = save_uploaded_file(file, subfolder=folder)
    if not url:
        allowed = ", ".join(current_app.config["ALLOWED_EXTENSIONS"])
        return error_response(f"Invalid file type. Allowed: {allowed}")

    return success_response(
        data={"url": url},
        message="Image uploaded successfully",
        status_code=201,
    )
    file = request.files.get("file")
    if not file or not file.filename:
        return error_response("No file provided. Use field name 'file'")

    folder = request.args.get("folder", "products")
    # Whitelist allowed folders
    if folder not in ("products", "misc"):
        folder = "products"

    url = save_uploaded_file(file, subfolder=folder)
    if not url:
        allowed = ", ".join(current_app.config["ALLOWED_EXTENSIONS"])
        return error_response(f"Invalid file type. Allowed: {allowed}")

    return success_response(
        data={"url": url},
        message="Image uploaded successfully",
        status_code=201,
    )


@upload_bp.delete("/image")
@admin_required
def delete_image():
    """
    Delete an uploaded image
    ---
    tags:
      - Upload
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            url:
              type: string
              example: "/uploads/products/uuid.jpg"
    responses:
      200:
        description: Image deleted successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Image deleted successfully"
      400:
        description: Bad request
      401:
        description: Unauthorized
    """
    data = request.get_json(silent=True) or {}
    url  = data.get("url")
    if not url:
        return error_response("'url' field is required")
    data = request.get_json(silent=True) or {}
    url  = data.get("url")
    if not url:
        return error_response("'url' field is required")

    delete_file(url)
    return success_response(message="Image deleted successfully")
