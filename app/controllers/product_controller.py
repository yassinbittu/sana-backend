from flask import request
from app import db
from app.models.product import Product
from app.utils.helpers import (
    success_response, error_response, paginated_response,
    validate_required, save_uploaded_file, delete_file
)


def get_all_products():
    page     = request.args.get("page",     1,   type=int)
    per_page = request.args.get("per_page", 12,  type=int)
    per_page = min(per_page, 50)  # cap

    query = Product.query.filter_by(is_active=True)

    # ── Filters ───────────────────────────────────────────
    occasion = request.args.get("occasion")
    fabric   = request.args.get("fabric")
    color    = request.args.get("color")
    in_stock = request.args.get("in_stock")
    is_new   = request.args.get("is_new")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    search   = request.args.get("search")

    if occasion:  query = query.filter(Product.occasion.ilike(f"%{occasion}%"))
    if fabric:    query = query.filter(Product.fabric.ilike(f"%{fabric}%"))
    if color:     query = query.filter(Product.color.ilike(f"%{color}%"))
    if in_stock is not None:
        query = query.filter(Product.in_stock == (in_stock.lower() == "true"))
    if is_new is not None:
        query = query.filter(Product.is_new == (is_new.lower() == "true"))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%"),
            )
        )

    # ── Sort ──────────────────────────────────────────────
    sort = request.args.get("sort", "newest")
    if sort == "price_asc":   query = query.order_by(Product.price.asc())
    elif sort == "price_desc": query = query.order_by(Product.price.desc())
    elif sort == "newest":     query = query.order_by(Product.created_at.desc())
    else:                      query = query.order_by(Product.created_at.desc())

    return paginated_response(query, page, per_page, lambda p: p.to_dict())


def get_product(product_id: int):
    product = Product.query.filter_by(id=product_id, is_active=True).first()
    if not product:
        return error_response("Product not found", 404)
    return success_response(data={"product": product.to_dict()})


def create_product():
    # Support both JSON and multipart/form-data (with image)
    if request.content_type and "multipart" in request.content_type:
        data = request.form.to_dict()
        file = request.files.get("image")
    else:
        data = request.get_json(silent=True) or {}
        file = None

    missing = validate_required(data, ["name", "price"])
    if missing:
        return error_response(f"Missing required fields: {', '.join(missing)}")

    try:
        price = float(data["price"])
    except (ValueError, TypeError):
        return error_response("Price must be a valid number")

    original_price = None
    if data.get("original_price"):
        try:
            original_price = float(data["original_price"])
        except (ValueError, TypeError):
            return error_response("original_price must be a valid number")

    # ── Handle image upload ───────────────────────────────
    image_url = None
    if file:
        image_url = save_uploaded_file(file, subfolder="products")
        if not image_url:
            return error_response("Invalid image file type. Allowed: png, jpg, jpeg, gif, webp")

    # Override with URL string if provided
    if data.get("image_url"):
        image_url = data["image_url"]

    # ── Discount auto-calc ────────────────────────────────
    discount = None
    if original_price and original_price > price:
        discount = int(round((original_price - price) / original_price * 100))

    product = Product(
        name=data["name"].strip(),
        description=data.get("description"),
        price=price,
        original_price=original_price,
        discount=discount,
        image_url=image_url,
        occasion=data.get("occasion"),
        fabric=data.get("fabric"),
        color=data.get("color"),
        care=data.get("care"),
        in_stock=str(data.get("in_stock", "true")).lower() != "false",
        is_new=str(data.get("is_new", "false")).lower() == "true",
    )

    db.session.add(product)
    db.session.commit()
    return success_response(
        data={"product": product.to_dict()},
        message="Product created successfully",
        status_code=201,
    )


def update_product(product_id: int):
    product = Product.query.get(product_id)
    if not product:
        return error_response("Product not found", 404)

    if request.content_type and "multipart" in request.content_type:
        data = request.form.to_dict()
        file = request.files.get("image")
    else:
        data = request.get_json(silent=True) or {}
        file = None

    # ── Apply updates ─────────────────────────────────────
    if "name"        in data: product.name        = data["name"].strip()
    if "description" in data: product.description = data["description"]
    if "occasion"    in data: product.occasion    = data["occasion"]
    if "fabric"      in data: product.fabric      = data["fabric"]
    if "color"       in data: product.color       = data["color"]
    if "care"        in data: product.care        = data["care"]
    if "in_stock"    in data: product.in_stock    = str(data["in_stock"]).lower() != "false"
    if "is_new"      in data: product.is_new      = str(data["is_new"]).lower() == "true"
    if "is_active"   in data: product.is_active   = str(data["is_active"]).lower() != "false"

    if "price" in data:
        try:
            product.price = float(data["price"])
        except (ValueError, TypeError):
            return error_response("Price must be a valid number")

    if "original_price" in data:
        try:
            product.original_price = float(data["original_price"]) if data["original_price"] else None
        except (ValueError, TypeError):
            return error_response("original_price must be a valid number")

    # Recalculate discount
    if product.original_price and product.original_price > product.price:
        product.discount = int(round(
            (float(product.original_price) - float(product.price)) / float(product.original_price) * 100
        ))
    else:
        product.discount = None

    # ── New image upload ──────────────────────────────────
    if file:
        new_url = save_uploaded_file(file, subfolder="products")
        if not new_url:
            return error_response("Invalid image file type")
        delete_file(product.image_url)     # remove old image
        product.image_url = new_url
    elif "image_url" in data:
        product.image_url = data["image_url"]

    db.session.commit()
    return success_response(
        data={"product": product.to_dict()},
        message="Product updated successfully",
    )


def delete_product(product_id: int):
    product = Product.query.get(product_id)
    if not product:
        return error_response("Product not found", 404)

    # Soft delete
    product.is_active = False
    db.session.commit()
    return success_response(message="Product deleted successfully")


def get_product_filters():
    """Return distinct filter values for the frontend dropdowns."""
    occasions = [r[0] for r in db.session.query(Product.occasion).filter(
        Product.is_active == True, Product.occasion.isnot(None)
    ).distinct().all()]

    fabrics = [r[0] for r in db.session.query(Product.fabric).filter(
        Product.is_active == True, Product.fabric.isnot(None)
    ).distinct().all()]

    colors = [r[0] for r in db.session.query(Product.color).filter(
        Product.is_active == True, Product.color.isnot(None)
    ).distinct().all()]

    return success_response(data={
        "occasions": sorted(occasions),
        "fabrics":   sorted(fabrics),
        "colors":    sorted(colors),
    })
