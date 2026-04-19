import os
import uuid
import random
import string
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
from flask import current_app


# ── Response helpers ──────────────────────────────────────────────────────────

def success_response(data=None, message="Success", status_code=200, **kwargs):
    resp = {"success": True, "message": message}
    if data is not None:
        resp["data"] = data
    resp.update(kwargs)
    return resp, status_code


def error_response(message="An error occurred", status_code=400, errors=None):
    resp = {"success": False, "message": message}
    if errors:
        resp["errors"] = errors
    return resp, status_code


def paginated_response(query, page, per_page, serializer_fn):
    """Run a paginated query and return standard envelope."""
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        "success": True,
        "data": [serializer_fn(item) for item in paginated.items],
        "pagination": {
            "page":        paginated.page,
            "per_page":    paginated.per_page,
            "total":       paginated.total,
            "pages":       paginated.pages,
            "has_next":    paginated.has_next,
            "has_prev":    paginated.has_prev,
            "next_page":   paginated.next_num,
            "prev_page":   paginated.prev_num,
        },
    }, 200


# ── Order number ──────────────────────────────────────────────────────────────

def generate_order_number() -> str:
    """e.g. SANA-20240115-X7K2"""
    date_part   = datetime.now(timezone.utc).strftime("%Y%m%d")
    random_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"SANA-{date_part}-{random_part}"


# ── File upload ───────────────────────────────────────────────────────────────

def allowed_file(filename: str) -> bool:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def save_uploaded_file(file, subfolder="products") -> str | None:
    """
    Saves an uploaded file to UPLOAD_FOLDER/<subfolder>/<uuid>.<ext>.
    Returns the public URL path or None on failure.
    """
    if not file or not file.filename:
        return None
    if not allowed_file(file.filename):
        return None

    ext      = secure_filename(file.filename).rsplit(".", 1)[-1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    folder   = os.path.join(current_app.config["UPLOAD_FOLDER"], subfolder)
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, filename))

    # Return relative URL (Flask serves /uploads/... as static)
    return f"/uploads/{subfolder}/{filename}"


def delete_file(url_path: str):
    """Remove a previously uploaded file given its URL path."""
    if not url_path:
        return
    rel = url_path.lstrip("/uploads/")
    full = os.path.join(current_app.config["UPLOAD_FOLDER"], rel)
    if os.path.exists(full):
        os.remove(full)


# ── Validation ────────────────────────────────────────────────────────────────

def validate_phone(phone: str) -> bool:
    digits = "".join(filter(str.isdigit, phone))
    return 10 <= len(digits) <= 12


def validate_required(data: dict, fields: list) -> list:
    """Return list of missing field names.

    Treat fields as missing only when they are not present, None, or empty strings.
    This avoids rejecting valid falsey values such as 0 or False.
    """
    missing = []
    for field in fields:
        if field not in data:
            missing.append(field)
            continue
        value = data[field]
        if value is None:
            missing.append(field)
            continue
        if isinstance(value, str) and value.strip() == "":
            missing.append(field)
    return missing
