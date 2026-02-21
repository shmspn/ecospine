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
from werkzeug.utils import secure_filename
from uuid import uuid4
from app.models import User, Product, Settings, ProductImage
from app.extensions import db
from app.utils import get_sizes, apply_product_filters
from functools import wraps
import json, os

PER_PAGE = 20

# Allowed image extensions
ALLOWED_IMAGE_EXTS = {"png", "jpg", "jpeg", "gif", "webp", "avif"}


def save_image(file_storage):
    """Validate and save an uploaded image, return the saved filename.

    Raises ValueError on invalid files.
    """
    if not file_storage or not getattr(file_storage, "filename", None):
        raise ValueError("No file")

    filename = secure_filename(file_storage.filename)
    if "." not in filename:
        raise ValueError("Missing extension")

    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTS:
        raise ValueError("Invalid extension")

    # Basic MIME check
    mimetype = getattr(file_storage, "mimetype", "") or file_storage.content_type or ""
    if not mimetype.startswith("image/"):
        raise ValueError("Invalid mime type")

    upload_dir = current_app.config.get("UPLOAD_FOLDER")
    if not upload_dir:
        raise ValueError("Upload folder not configured")

    os.makedirs(upload_dir, exist_ok=True)

    unique_name = f"{uuid4().hex}.{ext}"
    dest_path = os.path.join(upload_dir, unique_name)

    # Save file to disk
    file_storage.save(dest_path)

    return unique_name


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
    page = request.args.get("page", 1, type=int)
    sizes = get_sizes(Product)

    query = Product.query
    query, selected_sizes = apply_product_filters(query, request.args)
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)

    return render_template(
        'admin/admin_panel.html',
        page='products',
        products=pagination.items,
        pagination=pagination,
        sizes=sizes,
        selected_sizes=selected_sizes,
    )


@admin_bp.route('/add_users', methods=['GET', 'POST'])
@admin_required
def add_users():
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = (request.form.get('password') or '').strip()
        role = request.form.get('role', 'moderator')

        # Validation
        if not username or len(username) < 3:
            flash("Username kamida 3 ta belgi bo'lishi kerak", 'warning')
            return redirect(url_for('admin.users'))
        if not password or len(password) < 4:
            flash("Parol kamida 4 ta belgi bo'lishi kerak", 'warning')
            return redirect(url_for('admin.users'))
        if User.query.filter_by(username=username).first():
            flash("Bu username allaqachon mavjud", 'warning')
            return redirect(url_for('admin.users'))

        user = User(username=username, role=role)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Foydalanuvchi yaratildi', 'success')
        return redirect(url_for('admin.users'))
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
@moderator_required
def products():
    page = request.args.get("page", 1, type=int)

    query = Product.query
    query, selected_sizes = apply_product_filters(query, request.args)
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)

    sizes = get_sizes(Product)

    return render_template(
        "admin/admin_panel.html",
        page="products",
        products=pagination.items,
        pagination=pagination,
        sizes=sizes,
        selected_sizes=selected_sizes,
    )



@admin_bp.route("/update_product", methods=["POST"])
@moderator_required
def update_product():
    product_id = request.form.get("product_id")
    product = Product.query.get_or_404(product_id)

    product.title = (request.form.get("title") or "").strip()
    product.size = (request.form.get("size") or "").strip()
    product.price = max(0, int(request.form.get("price") or 0))
    product.discount_percent = max(0, min(100, int(request.form.get("discount_percent") or 0)))
    product.description = (request.form.get("description") or "").strip()
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
            try:
                filename = save_image(img)
            except ValueError:
                continue
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
        title = (request.form.get('title') or '').strip()
        description = (request.form.get('description') or '').strip()
        size = (request.form.get('size') or '').strip()
        images = request.files.getlist("images")

        try:
            price = max(0, int(request.form.get('price') or 0))
        except (ValueError, TypeError):
            price = 0

        try:
            d = max(0, min(100, int(request.form.get('discount_percent') or 0)))
        except (ValueError, TypeError):
            d = 0

        # Validation
        if not title:
            flash("Mahsulot nomi kiritilishi shart", 'warning')
            return redirect(url_for('admin.products'))
        if price <= 0:
            flash("Narx musbat bo'lishi kerak", 'warning')
            return redirect(url_for('admin.products'))

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
                try:
                    filename = save_image(img)
                except ValueError:
                    # skip invalid uploads
                    continue
                db.session.add(ProductImage(
                    product_id=product.id,
                    filename=filename,
                    is_main=(i == 0)  # birinchi rasm main
                ))

        db.session.commit()

        flash('Product added successfully', 'success')
        return redirect(url_for('admin.products'))
    # For GET requests, show the products page (the form is in the admin panel template)
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
@moderator_required
def toggle_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = not bool(product.is_active)
    db.session.commit()
    return redirect(url_for("admin.products"))
