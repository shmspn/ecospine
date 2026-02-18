from app.extensions import db

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
