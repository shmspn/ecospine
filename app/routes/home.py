from flask import Blueprint, render_template, request
from app.models import Product, Settings
from sqlalchemy import or_
from app.extentions import db

home_bp = Blueprint('home', __name__)

@home_bp.route('/', methods=['GET'])
def index():
    q = (request.args.get("q") or "").strip()
    sort = request.args.get("sort") or "new"

    # price range
    min_price = (request.args.get("min_price") or "").strip()
    max_price = (request.args.get("max_price") or "").strip()

    # multi size
    selected_sizes = [s.strip() for s in request.args.getlist("sizes") if s.strip()]

    query = Product.query.filter(Product.is_active.is_(True))

    # search
    if q:
        like = f"%{q}%"
        query = query.filter(or_(
            Product.title.ilike(like),
            Product.description.ilike(like),
            Product.size.ilike(like),
        ))
    
    # sizes (multi)
    if selected_sizes:
        query = query.filter(Product.size.in_(selected_sizes))



    # Price filter (CHEGIRMALI NARX bo'yicha)
    if min_price:
        try:
            query = query.filter(Product.final_price >= int(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            query = query.filter(Product.final_price <= int(max_price))
        except ValueError:
            pass
    
    # Sort ham final_price bo'yicha
    if sort == "price_asc":
        query = query.order_by(Product.final_price.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.final_price.desc())
    elif sort == "discount_desc":
        query = query.order_by(Product.discount_percent.desc())
    else:
        query = query.order_by(Product.id.desc())

    products = query.all()

    sizes = [
        (r[0] or "").strip()
        for r in db.session.query(Product.size).distinct().order_by(Product.size).all()
        if (r[0] or "").strip()
    ]

    return render_template('main/home.html', products=products, sizes=sizes, selected_sizes=selected_sizes)

@home_bp.get("/products/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("main/product_detail.html", product=product)
