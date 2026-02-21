from app.extensions import db
from app.models import Product
from sqlalchemy import or_


def get_sizes(Product):
    """Return a list of distinct non-empty sizes for Product model.

    Usage: `sizes = get_sizes(Product)`
    """
    sizes = [
        (r[0] or "").strip()
        for r in db.session.query(Product.size).distinct().order_by(Product.size).all()
        if (r[0] or "").strip()
    ]
    return sizes


def apply_product_filters(query, args, use_final_price=False):
    """Apply search, size, price, discount filters and sorting to a Product query.

    Parameters:
        query: SQLAlchemy query on Product
        args: request.args (ImmutableMultiDict)
        use_final_price: if True, filter/sort by final_price (with discount);
                         otherwise use raw price

    Returns:
        filtered and sorted query
    """
    q = (args.get("q") or "").strip()
    sort = args.get("sort") or "new"
    min_price = (args.get("min_price") or "").strip()
    max_price = (args.get("max_price") or "").strip()
    discount = args.get("discount")

    # Size parameter name differs: 'sizes' for home, 'size' for admin
    selected_sizes = [s.strip() for s in args.getlist("sizes") if s and s.strip()]
    if not selected_sizes:
        selected_sizes = [s.strip() for s in args.getlist("size") if s and s.strip()]

    # Text search
    if q:
        like = f"%{q}%"
        query = query.filter(or_(
            Product.title.ilike(like),
            Product.description.ilike(like),
            Product.size.ilike(like),
        ))

    # Size filter (multi)
    if selected_sizes:
        query = query.filter(Product.size.in_(selected_sizes))

    # Discount filter
    if discount == "1":
        query = query.filter(Product.discount_percent > 0)

    # Price field to use
    price_field = Product.final_price if use_final_price else Product.price

    # Price range
    if min_price:
        try:
            query = query.filter(price_field >= int(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            query = query.filter(price_field <= int(max_price))
        except ValueError:
            pass

    # Sorting
    if sort == "price_asc":
        query = query.order_by(price_field.asc())
    elif sort == "price_desc":
        query = query.order_by(price_field.desc())
    elif sort == "discount_desc":
        query = query.order_by(Product.discount_percent.desc())
    else:
        query = query.order_by(Product.id.desc())

    return query, selected_sizes
