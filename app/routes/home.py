from flask import Blueprint, render_template, request
from app.models import Product
from app.utils import get_sizes, apply_product_filters

home_bp = Blueprint('home', __name__)

PER_PAGE = 20

@home_bp.route('/', methods=['GET'])
def index():
    page = request.args.get("page", 1, type=int)

    query = Product.query.filter(Product.is_active.is_(True))
    query, selected_sizes = apply_product_filters(query, request.args, use_final_price=True)

    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)

    sizes = get_sizes(Product)

    return render_template(
        'main/home.html',
        products=pagination.items,
        pagination=pagination,
        sizes=sizes,
        selected_sizes=selected_sizes,
    )
