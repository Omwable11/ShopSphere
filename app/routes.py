import os
import uuid

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from werkzeug.utils import secure_filename

from app import app, db
from app.models import (
    User,
    Product,
    Category,
    Order,
    OrderItem,
    Wishlist,
    Review
)

from flask import make_response
from reportlab.pdfgen import canvas
from io import BytesIO

# -----------------------------
# Image Upload
# -----------------------------

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif"
}


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# -----------------------------
# Home
# -----------------------------

@app.route("/")
def home():

    return render_template("home.html")


# -----------------------------
# Products
# -----------------------------

@app.route("/products")
def product_list():

    search = request.args.get("search", "")
    category = request.args.get("category", "")
    sort = request.args.get("sort", "")

    products = Product.query

    if search:
        products = products.filter(Product.name.ilike(f"%{search}%"))

    if category:
        products = products.filter(Product.category_id == int(category))

    if sort == "low":
        products = products.order_by(Product.price.asc())

    elif sort == "high":
        products = products.order_by(Product.price.desc())

    products = products.all()

    categories = Category.query.all()

    return render_template(
        "products.html",
        products=products,
        categories=categories,
        search=search,
        category=category,
        sort=sort
    )

@app.route("/products/<int:product_id>")
def product_detail(product_id):

    product = Product.query.get_or_404(product_id)

    reviews = Review.query.filter_by(
        product_id=product.id
    ).order_by(
        Review.created_at.desc()
    ).all()

    return render_template(
        "product_detail.html",
        product=product,
        reviews=reviews
    )

@app.route("/review/<int:product_id>", methods=["POST"])
def add_review(product_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    rating = int(request.form["rating"])
    comment = request.form["comment"]

    existing = Review.query.filter_by(
        user_id=session["user_id"],
        product_id=product_id
    ).first()

    if existing:
        flash("You have already reviewed this product.", "warning")
        return redirect(url_for("product_detail", product_id=product_id))

    review = Review(
        user_id=session["user_id"],
        product_id=product_id,
        rating=rating,
        comment=comment
    )

    db.session.add(review)
    db.session.commit()

    flash("Review submitted successfully!", "success")

    return redirect(url_for("product_detail", product_id=product_id))


# -----------------------------
# Cart
# -----------------------------

@app.route("/add-to-cart/<int:product_id>")
def add_to_cart(product_id):

    cart = session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:

        cart[product_id] += 1

    else:

        cart[product_id] = 1

    session["cart"] = cart

    flash("Product added to cart!", "success")

    return redirect(url_for("product_list"))


@app.route("/cart")
def cart():

    cart = session.get("cart", {})

    cart_items = []

    total = 0

    for product_id, quantity in cart.items():

        product = Product.query.get(int(product_id))

        if product:

            subtotal = product.price * quantity

            total += subtotal

            cart_items.append({

                "product": product,

                "quantity": quantity,

                "subtotal": subtotal

            })

    return render_template(

        "cart.html",

        cart_items=cart_items,

        total=total

    )


@app.route("/cart/increase/<int:product_id>")
def increase_quantity(product_id):

    cart = session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:

        cart[product_id] += 1

    session["cart"] = cart

    return redirect(url_for("cart"))


@app.route("/cart/decrease/<int:product_id>")
def decrease_quantity(product_id):

    cart = session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:

        cart[product_id] -= 1

        if cart[product_id] <= 0:

            del cart[product_id]

    session["cart"] = cart

    return redirect(url_for("cart"))


@app.route("/cart/remove/<int:product_id>")
def remove_from_cart(product_id):

    cart = session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:

        del cart[product_id]

    session["cart"] = cart

    flash("Product removed from cart.", "success")

    return redirect(url_for("cart"))


# -----------------------------
# Register
# -----------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]

        email = request.form["email"].strip().lower()

        password = request.form["password"]

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash("Email already registered!", "danger")

            return redirect(url_for("register"))

        user = User(

            username=username,

            email=email

        )

        user.set_password(password)

        db.session.add(user)

        db.session.commit()

        flash("Registration Successful!", "success")

        return redirect(url_for("login"))

    return render_template("register.html")


# -----------------------------
# Login
# -----------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()

        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):

            session["user_id"] = user.id

            session["username"] = user.username

            flash("Login Successful!", "success")

            return redirect(url_for("home"))

        flash("Invalid Email or Password.", "danger")

    return render_template("login.html")


# -----------------------------
# Logout
# -----------------------------

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully!", "success")

    return redirect(url_for("home"))

    # -----------------------------
# Checkout
# -----------------------------

@app.route("/checkout")
def checkout():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    cart = session.get("cart", {})

    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("product_list"))

    total = 0
    order_items = []

    for product_id, quantity in cart.items():

        product = Product.query.get(int(product_id))

        if not product:
            continue

        if product.stock < quantity:

            flash(
                f"Only {product.stock} item(s) available for {product.name}.",
                "danger"
            )

            return redirect(url_for("cart"))

        subtotal = product.price * quantity

        total += subtotal

        order_items.append({

            "product": product,

            "quantity": quantity,

            "price": product.price

        })

    order = Order(

        user_id=session["user_id"],

        total=total

    )

    db.session.add(order)
    db.session.commit()

    for item in order_items:

        order_item = OrderItem(

            order_id=order.id,

            product_id=item["product"].id,

            quantity=item["quantity"],

            price=item["price"]

        )

        db.session.add(order_item)

        item["product"].stock -= item["quantity"]

    db.session.commit()

    session["cart"] = {}

    flash("Order placed successfully!", "success")

    return redirect(url_for("orders"))


# -----------------------------
# Orders
# -----------------------------

@app.route("/orders")
def orders():

    if "user_id" not in session:
        return redirect(url_for("login"))

    orders = Order.query.filter_by(

        user_id=session["user_id"]

    ).order_by(

        Order.created_at.desc()

    ).all()

    return render_template(

        "orders.html",

        orders=orders

    )


# -----------------------------
# Admin Dashboard
# -----------------------------

@app.route("/admin")
def admin_dashboard():

    if "user_id" not in session:

        flash("Please login first.", "warning")

        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    if not user.is_admin:

        flash("Access Denied!", "danger")

        return redirect(url_for("home"))

    product_count = Product.query.count()

    user_count = User.query.count()

    order_count = Order.query.count()

    total_revenue = db.session.query(
    db.func.sum(Order.total)
    ).scalar() or 0

    recent_orders = Order.query.order_by(
    Order.created_at.desc()
    ).limit(5).all()

    return render_template(
    "admin/dashboard.html",
    product_count=product_count,
    user_count=user_count,
    order_count=order_count,
    total_revenue=total_revenue,
    recent_orders=recent_orders
)

# -----------------------------
# Add Product
# -----------------------------

@app.route("/admin/add-product", methods=["GET", "POST"])
def add_product():

    if "user_id" not in session:

        flash("Please login first.", "warning")

        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    if not user.is_admin:

        flash("Access Denied!", "danger")

        return redirect(url_for("home"))

    categories = Category.query.all()

    if request.method == "POST":

        name = request.form["name"]

        description = request.form["description"]

        price = float(request.form["price"])

        stock = int(request.form["stock"])

        category_id = int(request.form["category"])

        filename = ""

        image = request.files.get("image")

        if image and image.filename != "":

            if not allowed_file(image.filename):

                flash(
                    "Only PNG, JPG, JPEG and GIF images are allowed.",
                    "danger"
                )

                return redirect(request.url)

            filename = (
                uuid.uuid4().hex
                + "_"
                + secure_filename(image.filename)
            )

            image.save(

                os.path.join(

                    app.config["UPLOAD_FOLDER"],

                    filename

                )

            )

        product = Product(

            name=name,

            description=description,

            price=price,

            stock=stock,

            image=filename,

            category_id=category_id

        )

        db.session.add(product)

        db.session.commit()

        flash("Product Added Successfully!", "success")

        return redirect(url_for("manage_products"))

    return render_template(

        "admin/add_product.html",

        categories=categories

    )

# -----------------------------
# Manage Products
# -----------------------------

@app.route("/admin/products")
def manage_products():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    if not user.is_admin:
        flash("Access Denied!", "danger")
        return redirect(url_for("home"))

    products = Product.query.order_by(Product.id.desc()).all()

    return render_template(
        "admin/manage_products.html",
        products=products
    )


@app.route("/admin/orders")
def manage_orders():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    if not user.is_admin:
        flash("Access Denied!", "danger")
        return redirect(url_for("home"))

    orders = Order.query.order_by(
        Order.created_at.desc()
    ).all()

    return render_template(
        "admin/manage_orders.html",
        orders=orders
    )

@app.route("/admin/update-order/<int:order_id>", methods=["POST"])
def update_order_status(order_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    if not user.is_admin:
        flash("Access Denied!", "danger")
        return redirect(url_for("home"))

    order = Order.query.get_or_404(order_id)

    order.status = request.form["status"]

    db.session.commit()

    flash("Order status updated successfully!", "success")

    return redirect(url_for("manage_orders"))


# -----------------------------
# Edit Product
# -----------------------------

@app.route("/admin/edit-product/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    if not user.is_admin:
        return redirect(url_for("home"))

    product = Product.query.get_or_404(product_id)

    categories = Category.query.all()

    if request.method == "POST":

        product.name = request.form["name"]
        product.description = request.form["description"]
        product.price = float(request.form["price"])
        product.stock = int(request.form["stock"])
        product.category_id = int(request.form["category"])

        image = request.files.get("image")

        if image and image.filename != "":

            if allowed_file(image.filename):

                # Delete old image
                if product.image:

                    old_path = os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        product.image
                    )

                    if os.path.exists(old_path):
                        os.remove(old_path)

                filename = (
                    uuid.uuid4().hex
                    + "_"
                    + secure_filename(image.filename)
                )

                image.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        filename
                    )
                )

                product.image = filename

            else:

                flash(
                    "Only PNG, JPG, JPEG and GIF files are allowed.",
                    "danger"
                )

                return redirect(request.url)

        db.session.commit()

        flash("Product Updated Successfully!", "success")

        return redirect(url_for("manage_products"))

    return render_template(
        "admin/edit_product.html",
        product=product,
        categories=categories
    )


# -----------------------------
# Delete Product
# -----------------------------

@app.route("/admin/delete-product/<int:product_id>")
def delete_product(product_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    if not user.is_admin:
        return redirect(url_for("home"))

    product = Product.query.get_or_404(product_id)

    # Delete image
    if product.image:

        image_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            product.image
        )

        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(product)

    db.session.commit()

    flash("Product Deleted Successfully!", "success")

    return redirect(url_for("manage_products"))

@app.route("/wishlist/add/<int:product_id>")
def add_to_wishlist(product_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    exists = Wishlist.query.filter_by(
        user_id=session["user_id"],
        product_id=product_id
    ).first()

    if exists:
        flash("Already in wishlist.", "info")
        return redirect(url_for("product_list"))

    item = Wishlist(
        user_id=session["user_id"],
        product_id=product_id
    )

    db.session.add(item)
    db.session.commit()

    flash("Added to wishlist.", "success")

    return redirect(url_for("product_list"))

@app.route("/wishlist")
def wishlist():

    if "user_id" not in session:
        return redirect(url_for("login"))

    items = Wishlist.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "wishlist.html",
        items=items
    )

@app.route("/wishlist/remove/<int:id>")
def remove_wishlist(id):

    item = Wishlist.query.get_or_404(id)

    db.session.delete(item)

    db.session.commit()

    flash("Removed from wishlist.", "success")

    return redirect(url_for("wishlist"))

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get_or_404(session["user_id"])

    return render_template(
        "profile.html",
        user=user
    )

@app.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get_or_404(session["user_id"])

    if request.method == "POST":

        user.username = request.form["username"]
        user.email = request.form["email"]

        image = request.files.get("profile_image")

        if image and image.filename != "":

            if not allowed_file(image.filename):

                flash("Only PNG, JPG, JPEG and GIF images are allowed.", "danger")
                return redirect(request.url)

            # Delete old image
            if user.profile_image != "default.png":

                old_path = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    "profile_images",
                    user.profile_image
                )

                if os.path.exists(old_path):
                    os.remove(old_path)

            filename = (
                uuid.uuid4().hex
                + "_"
                + secure_filename(image.filename)
            )

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    "profile_images",
                    filename
                )
            )

            user.profile_image = filename

        db.session.commit()

        session["username"] = user.username

        flash("Profile updated successfully!", "success")

        return redirect(url_for("profile"))

    return render_template(
        "edit_profile.html",
        user=user
    )

@app.route("/change-password", methods=["GET", "POST"])
def change_password():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get_or_404(session["user_id"])

    if request.method == "POST":

        old_password = request.form["old_password"]
        new_password = request.form["new_password"]

        if not user.check_password(old_password):

            flash("Old password is incorrect.", "danger")
            return redirect(request.url)

        user.set_password(new_password)

        db.session.commit()

        flash("Password changed successfully!", "success")

        return redirect(url_for("profile"))

    return render_template("change_password.html")

@app.route("/invoice/<int:order_id>")
def download_invoice(order_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    order = Order.query.get_or_404(order_id)

    # Prevent users from downloading someone else's invoice
    if order.user_id != session["user_id"]:
        flash("Access Denied!", "danger")
        return redirect(url_for("orders"))

    buffer = BytesIO()

    pdf = canvas.Canvas(buffer)

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(180, 800, "ShopSphere Invoice")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 760, f"Invoice ID : {order.id}")
    pdf.drawString(50, 740, f"Customer : {order.user.username}")
    pdf.drawString(50, 720, f"Date : {order.created_at.strftime('%d-%m-%Y %H:%M')}")

    pdf.line(50, 700, 550, 700)

    y = 670

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "Product")
    pdf.drawString(300, y, "Qty")
    pdf.drawString(400, y, "Price")

    y -= 25

    pdf.setFont("Helvetica", 12)

    for item in order.items:

        pdf.drawString(50, y, item.product.name)
        pdf.drawString(300, y, str(item.quantity))
        pdf.drawString(400, y, f"₹{item.price}")

        y -= 20

    pdf.line(50, y, 550, y)

    y -= 30

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, f"Total : ₹{order.total}")

    pdf.save()

    buffer.seek(0)

    response = make_response(buffer.read())

    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = (
        f"attachment; filename=Invoice_{order.id}.pdf"
    )

    return response