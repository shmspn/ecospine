from flask import (
    Blueprint, 
    request, 
    session, 
    flash, 
    redirect, 
    url_for, 
    render_template,
    current_app
)
from werkzeug.utils import save_upload
from app.models import User, Product, Settings, ProductImage
from app.extentions import db
from functools import wraps
from sqlalchemy import or_
import json, os


admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = user.role
            flash('Login successful!', 'success')
            return redirect(url_for('admin.admin_panel'))
        else:
            flash('Username yoki password xato', 'danger')
            return redirect(url_for('admin.login'))
        
    return render_template('admin/login.html')


@admin_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('admin.login'))


# -------------------
#  Decorators
# -------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Avval login qiling', 'warning')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Sizga ruxsat yo\'q', 'danger')
            return redirect(url_for('admin.admin_panel'))
        return f(*args, **kwargs)
    return decorated

def moderator_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') not in ['admin', 'moderator']:
            flash('Sizga ruxsat yo\'q', 'danger')
            return redirect(url_for('home.index'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/settings", methods=["GET", "POST"])
@moderator_required
def settings():
    s = Settings.query.first()
    if not s:
        s = Settings(usd_to_uzs=12500)
        db.session.add(s)
        db.session.commit()
    if request.method == 'POST':
        rate = request.form.get('usd_to_uzs', type=int)
        if not rate or rate <= 0:
            flash("Kurs noto‘g‘ri.", "warning")
            return redirect(url_for("admin.settings"))
        
        s.usd_to_uzs = rate
        db.session.commit()
        flash("Kurs saqlandi.", "success")
        return redirect(url_for("admin.settings"))
    
    return render_template("admin/admin_panel.html", page="settings", settings=s)


@admin_bp.route('/')
@moderator_required
def admin_panel():
    
    sizes = [
        (r[0] or "").strip()
        for r in db.session.query(Product.size).distinct().order_by(Product.size).all()
        if (r[0] or "").strip()
    ]

    products = Product.query.order_by(Product.id.desc()).all()
    return render_template('admin/admin_panel.html', page='products', products=products, sizes=sizes)


@admin_bp.route('/add_users', methods=['GET', 'POST'])
@admin_required
def add_users():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        user = User(username=username, role=role)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Create user', 'success')
        return redirect(url_for('admin.users'))
    


@admin_bp.route('/users')
@login_required
def users():
    all_users = User.query.order_by(User.id.desc()).all()
    return render_template('admin/admin_panel.html', page="users", users=all_users)


@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)            
    db.session.commit()             
    flash(f'User "{user.username}" o\'chirildi', 'success')
    return redirect(url_for('admin.users'))



@admin_bp.route("/products", methods=["GET"])
def products():
    q = (request.args.get("q") or "").strip()
    discount = request.args.get("discount")  # "1" bo'ladi
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")
    sort = request.args.get("sort") or "new"

    selected_sizes = [s.strip() for s in request.args.getlist("size") if s and s.strip()]

    query = Product.query

    if q:
        like = f"%{q}%"
        query = query.filter(or_(
            Product.title.ilike(like),
            Product.description.ilike(like),
            Product.size.ilike(like),
        ))

    if selected_sizes:
            query = query.filter(Product.size.in_(selected_sizes))

    if discount == "1":
        query = query.filter((Product.discount_percent or 0) > 0)

    if min_price:
        try:
            query = query.filter(Product.price >= int(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            query = query.filter(Product.price <= int(max_price))
        except ValueError:
            pass

    if sort == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort == "discount_desc":
        query = query.order_by(Product.discount_percent.desc())
    else:
        query = query.order_by(Product.id.desc())

    products = query.order_by(Product.id.desc()).all()

    sizes = [
        (r[0] or "").strip()
        for r in db.session.query(Product.size).distinct().order_by(Product.size).all()
        if (r[0] or "").strip()
    ]
   
    return render_template(
        "admin/admin_panel.html",
        page="products",
        products=products,
        sizes=sizes,  # <= MUHIM: template'ga uzatyapmiz   
    )



@admin_bp.route("/update_product", methods=["POST"])
def update_product():
    product_id = request.form.get("product_id")
    product = Product.query.get_or_404(product_id)

    product.title = request.form.get("title")
    product.size = request.form.get("size")
    product.price = int(request.form.get("price") or 0)
    product.discount_percent = int(request.form.get("discount_percent") or 0)
    product.description = request.form.get("description")
    images = request.files.getlist("images")

    # ✅ delete qilingan rasmlar ro'yxati
    deleted = json.loads(request.form.get("delete_images", "[]"))

    if deleted:
        (ProductImage.query
            .filter(ProductImage.product_id == product.id,
                    ProductImage.filename.in_(deleted))
            .delete(synchronize_session=False)
        )
        db.session.commit()

    upload_dir = os.path.join(current_app.root_path, "static", "uploads")
    for fn in deleted:
        path = os.path.join(upload_dir, fn)
        if os.path.isfile(path):
            os.remove(path)

    has_main = any(img.is_main for img in product.images)

    for img in images:
        if img and img.filename:
            filename = save_upload(img, current_app.config["UPLOAD_FOLDER"])
            db.session.add(ProductImage(
                product_id=product.id,
                filename=filename,
                is_main=(not has_main)  # agar hali main bo'lmasa birinchisini main qil
            ))
            has_main = True

    db.session.commit()
    return redirect(url_for("admin.products"))

@admin_bp.route('/delete_product/<int:product_id>', methods=['POST'])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    title = product.title

    # 1) Shu product'ga tegishli rasmlar filename'larini yig'amiz
    images = ProductImage.query.filter_by(product_id=product.id).all()
    filenames = [img.filename for img in images if img.filename]

    # 2) Diskdan o'chiramiz
    upload_dir = os.path.join(current_app.root_path, "static", "uploads")
    for fn in filenames:
        # path traversal'dan saqlanish: faqat basename
        safe_name = os.path.basename(fn)
        path = os.path.join(upload_dir, safe_name)
        if os.path.isfile(path):
            try:
                os.remove(path)
            except OSError:
                pass  # xohlasangiz log yozing

    db.session.delete(product)
    db.session.commit()

    flash(f'"{product.title}" o\'chirildi', 'success')
    return redirect(url_for('admin.products'))




@admin_bp.route('/add_products', methods=['GET', 'POST'])
@moderator_required
def add_product():
    if request.method == 'POST':
        title = request.form.get('title')
        price = request.form.get('price', type=int)
        description = request.form.get('description')
        size = request.form.get("size")
        images = request.files.getlist("images")
        discount_percent = (request.form.get("discount_percent") or "").strip()
        
        try:
            d = int(discount_percent)
        except ValueError:
            d = 0


        product = Product(
            title=title, 
            price=price,
            size=size,
            description=description,
            discount_percent=d,
            created_by=session['user_id']
        )
        db.session.add(product)
        db.session.flush()

        for i, img in enumerate(images):
            if img and img.filename:
                filename = save_upload(img, current_app.config["UPLOAD_FOLDER"])
                db.session.add(ProductImage(
                    product_id=product.id,
                    filename=filename,
                    is_main=(i == 0)  # birinchi rasm main
                ))

        db.session.commit()

        flash('Product added successfully', 'success')
        return redirect(url_for('admin.products'))
    

    
@admin_bp.route('/products/<int:product_id>/discount', methods=['POST'])
@moderator_required
def set_discount(product_id):
    product = Product.query.get_or_404(product_id)

    d_raw = (request.form.get("discount_percent") or "").strip()

    try:
        d = int(d_raw)
    except ValueError:
        d = 0

    product.discount_percent = d
    db.session.commit()

    return redirect(url_for('admin.products'))


@admin_bp.route("/toggle_product/<int:product_id>", methods=["POST"])
def toggle_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = not bool(product.is_active)
    db.session.commit()
    return redirect(url_for("admin.products"))
