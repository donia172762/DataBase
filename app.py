from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
import json
import mysql.connector
import os
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = 'static/image'
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
import json
import mysql.connector

from functools import wraps
from flask import session, redirect, url_for, request, flash

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first to add items to cart.", "warning")

            next_url = request.referrer or url_for("shop")

            return redirect(url_for("login_by_role", role="customer", next=next_url))
        return f(*args, **kwargs)
    return decorated
app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.config["UPLOAD_FOLDER"] = os.path.join(
    BASE_DIR, "static", "uploads", "products"
)
app.secret_key = "labmart_secret_key_123"

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="0567431153donia123",
        database="labmart6_db"
    )
    # this page for anybody visit my website
@app.route('/')
def landing():
    return render_template('landing.html')
#--------------   signup --------------#
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        customer_name = request.form["customer_name"]
        city = request.form["city"]
        phone = request.form["phone"]
        email = request.form["email"]
        password = request.form["password"]

        pw_hash = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()

       
        cur.execute("SELECT customer_id FROM customer WHERE email=%s", (email,))
        if cur.fetchone():
            cur.close()
            conn.close()
            flash("Email already registered. Please login.", "danger")
            return redirect(url_for("login"))

        try:
            cur.execute("""
                INSERT INTO customer (customer_name, `type`, city, phone, email, password_hash)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (customer_name, "customer", city, phone, email, pw_hash))

            conn.commit()
            flash("Account created successfully. Please login.", "success")
            return redirect(url_for("login"))

        except mysql.connector.Error as e:
            flash(f"Database error: {e}", "danger")

        finally:
            cur.close()
            conn.close()

    return render_template("signup.html", title="Sign Up")

#--------------------#
  #---login
#----------------------#
@app.route("/login-role")
def login_role():
    return render_template("login_role.html", title="Choose Role")

@app.route("/login/<role>", methods=["GET", "POST"])
def login_by_role(role):

    if role not in ["admin", "supplier", "customer"]:
        flash("Invalid role.", "danger")
        return redirect(url_for("login_role"))

    next_page = request.args.get("next")

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM customer WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):

            
            if user["type"] != role:
                flash("Access denied for this role.", "danger")
                return redirect(url_for("login_by_role", role=role))

           
            session["user_id"] = user["customer_id"]
            session["user_name"] = user["customer_name"]
            session["user_type"] = user["type"]

            flash("Logged in successfully!", "success")

           
            if next_page:
                return redirect(next_page)

           
            if role == "admin":
                return redirect(url_for("admin_page"))
            elif role == "supplier":
                return redirect(url_for("suppliers"))
            else:
                return redirect(url_for("shop"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html", role=role, title="Login")

@app.route("/login")
def login():
    return redirect(url_for("login_by_role", role="customer"))

#--------------logout----------#
#--------------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("shop"))

#--------------admin----------#
#--------------------------

@app.route("/login/admin", methods=["GET", "POST"])
def login_admin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute(
            "SELECT admin_id, full_name FROM admin WHERE email=%s AND password=%s",
            (email, password)
        )
        admin = cur.fetchone()

        if admin:
            session["user_id"] = admin["admin_id"]
            session["role"] = "admin"
            return redirect(url_for("admin_home"))
        else:
            flash("Invalid admin credentials", "danger")

    return render_template("login_admin.html")
#----------------------------#
#        admin home
#----------------------------#
@app.route("/admin/home")
def admin_home():
   
    if "role" not in session or session["role"] != "admin":
        return redirect(url_for("login_admin"))

    return render_template("admin_home.html")

      #-----about us ---------#
@app.route('/about')
def about():
    return render_template('about.html')
# -----------------------
# Shop + Cart
# -----------------------
def get_cart():
    return session.get("cart", {})  # {product_id: qty}

def save_cart(cart):
    session["cart"] = cart


@app.route("/shop")
def shop():
    warehouse_id = request.args.get("warehouse_id")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if warehouse_id:
        cursor.execute("""
            SELECT p.*, ws.quantity_available
            FROM Product p
            JOIN WarehouseStock ws ON p.product_id = ws.product_id
            WHERE ws.warehouse_id = %s
        """, (warehouse_id,))
    else:
        cursor.execute("""
            SELECT p.*, ws.quantity_available
            FROM Product p
            JOIN WarehouseStock ws ON p.product_id = ws.product_id
        """)

    products = cursor.fetchall()

    cursor.execute("SELECT warehouse_id, warehouse_name FROM Warehouse")
    warehouses = cursor.fetchall()

    return render_template(
        "shop.html",
        products=products,
        warehouses=warehouses
    )


@app.route("/cart")
@login_required
def cart():
    cart = get_cart()
    cart_items = []
    subtotal = 0.0

    if cart:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        ids = list(cart.keys())
        placeholders = ",".join(["%s"] * len(ids))
        cur.execute(f"SELECT * FROM product WHERE product_id IN ({placeholders})", ids)
        products = cur.fetchall()
        cur.close()
        conn.close()

        prod_map = {p["product_id"]: p for p in products}

        for pid_str, qty in cart.items():
            pid = int(pid_str)
            p = prod_map.get(pid)
            if not p:
                continue

            try:
                price = float(p["unit_price_sell"])
            except (TypeError, ValueError):
                price = 0.0

            item_total = price * int(qty)
            subtotal += item_total

            cart_items.append({
                "product_id": pid,
                "name": p["product_name"],
                "price": price,
                "quantity": int(qty),
                "image": p.get("image", ""),
                "total": item_total
            })

    shipping = 0
    total = subtotal + shipping

    return render_template(
        "cart.html",
        cart_items=cart_items,
        subtotal=subtotal,
        shipping=shipping,
        total=total,
        title="Cart"
    )


@app.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    qty = int(request.form.get("qty", 1))
    cart = get_cart()

    pid_key = str(product_id)
    cart[pid_key] = cart.get(pid_key, 0) + qty

    save_cart(cart)
    flash("Added to cart.", "success")
    return redirect(url_for("shop"))


@app.route("/cart/remove/<int:product_id>")
def remove_from_cart(product_id):
    cart = get_cart()
    cart.pop(str(product_id), None)
    save_cart(cart)
    flash("Removed from cart.", "success")
    return redirect(url_for("cart"))
@app.context_processor
def inject_cart_count():
    cart = session.get("cart", {})
    cart_count = sum(cart.values())  
    return dict(cart_count=cart_count)

# -----------------------
# Checkout + Orders
# -----------------------
@app.route("/checkout", methods=["GET"])
@login_required
def checkout():
    cart = get_cart()
    if not cart:
        flash("Cart is empty.", "danger")
        return redirect(url_for("shop"))

    return render_template("checkout.html", title="Checkout")


import re
from datetime import datetime

def luhn_check(card_number: str) -> bool:
    digits = [int(d) for d in card_number if d.isdigit()][::-1]
    total = 0
    for i, d in enumerate(digits):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


@app.route("/checkout/save", methods=["POST"])
@login_required
def checkout_save():
    cart = get_cart()
    if not cart:
        flash("Cart is empty.", "danger")
        return redirect(url_for("shop"))

    full_name = request.form["full_name"].strip()
    address = request.form["address"].strip()
    phone = request.form["phone"].strip()
    payment_method = request.form["payment_method"]

    card_number = request.form.get("card_number", "").strip()
    card_name = request.form.get("card_name", "").strip()
    card_expiry = request.form.get("card_expiry", "").strip()
    card_cvv = request.form.get("card_cvv", "").strip()

    
    if len(full_name) < 3:
        flash("Please enter a valid full name.", "danger")
        return redirect(url_for("checkout"))

    if len(address) < 5:
        flash("Please enter a valid address.", "danger")
        return redirect(url_for("checkout"))

    if not re.fullmatch(r"[0-9+\s\-]{7,20}", phone):
        flash("Please enter a valid phone number.", "danger")
        return redirect(url_for("checkout"))

   
    if payment_method == "VISA":
        if not all([card_number, card_name, card_expiry, card_cvv]):
            flash("Please fill all card details.", "danger")
            return redirect(url_for("checkout"))

        
        card_number_clean = re.sub(r"\s+", "", card_number)
        if (not card_number_clean.isdigit()) or (not (13 <= len(card_number_clean) <= 19)):
            flash("Invalid card number.", "danger")
            return redirect(url_for("checkout"))

       
        if not luhn_check(card_number_clean):
            flash("Invalid card number.", "danger")
            return redirect(url_for("checkout"))

        if len(card_name) < 3:
            flash("Invalid name on card.", "danger")
            return redirect(url_for("checkout"))

        
        if not re.fullmatch(r"\d{3,4}", card_cvv):
            flash("Invalid CVV.", "danger")
            return redirect(url_for("checkout"))

        
        m = re.fullmatch(r"(0[1-9]|1[0-2])\/(\d{2})", card_expiry)
        if not m:
            flash("Expiry must be in MM/YY format.", "danger")
            return redirect(url_for("checkout"))

        mm = int(m.group(1))
        yy = int(m.group(2)) + 2000  

        now = datetime.now()
        if (yy < now.year) or (yy == now.year and mm < now.month):
            flash("Card is expired.", "danger")
            return redirect(url_for("checkout"))

    elif payment_method != "COD":
        flash("Invalid payment method.", "danger")
        return redirect(url_for("checkout"))

    DEFAULT_BRANCH_ID = 1

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    try:
        ids = [int(k) for k in cart.keys()]
        placeholders = ",".join(["%s"] * len(ids))
        cur.execute(
            f"SELECT product_id, unit_price_sell FROM product WHERE product_id IN ({placeholders})",
            ids
        )
        rows = cur.fetchall()
        price_map = {r["product_id"]: float(r["unit_price_sell"]) for r in rows}

        total_amount = sum(price_map[int(pid)] * int(qty) for pid, qty in cart.items())

        cur2 = conn.cursor()
        cur2.execute("""
            INSERT INTO salesorder
            (customer_id, branch_id, sales_date, total_amount, payment_status)
            VALUES (%s, %s, CURDATE(), %s, %s)
        """, (
            session["user_id"],
            DEFAULT_BRANCH_ID,
            total_amount,
            "Pending" if payment_method == "COD" else "Paid"
        ))

        so_id = cur2.lastrowid

        for pid, qty in cart.items():
            cur2.execute("""
                INSERT INTO salesorderitem
                (so_id, product_id, qty_sold, selling_price_per_unit)
                VALUES (%s, %s, %s, %s)
            """, (
                so_id,
                int(pid),
                int(qty),
                price_map[int(pid)]
            ))

        conn.commit()
        session.pop("cart", None)

        flash("Order placed successfully!", "success")
        return redirect(url_for("my_orders"))

    except Exception as e:
        conn.rollback()
        flash("Checkout failed.", "danger")
        return redirect(url_for("checkout"))

    finally:
        cur.close()
        conn.close()


@app.route("/my-orders")
@login_required
def my_orders():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT so_id, sales_date, total_amount, payment_status
        FROM salesorder
        WHERE customer_id=%s
        ORDER BY so_id DESC
    """, (session["user_id"],))

    orders = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("my_orders.html", orders=orders, title="My Orders")

@app.route("/my-orders/<int:so_id>")
@login_required
def order_details(so_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT * FROM salesorder
        WHERE so_id=%s AND customer_id=%s
    """, (so_id, session["user_id"]))

    order = cur.fetchone()
    if not order:
        cur.close()
        conn.close()
        flash("Order not found.", "danger")
        return redirect(url_for("my_orders"))

    cur.execute("""
        SELECT soi.*, p.product_name
        FROM salesorderitem soi
        JOIN product p ON p.product_id = soi.product_id
        WHERE soi.so_id=%s
    """, (so_id,))
    items = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("order_details.html", order=order, items=items, title="Order Details")
@app.context_processor
def inject_warehouses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT warehouse_id, warehouse_name FROM Warehouse")
    warehouses = cursor.fetchall()
    cursor.close()
    conn.close()
    return dict(warehouses=warehouses)
#-----------------------------------#
#        Branches
#-----------------------------------# 
from flask import request, render_template, redirect, url_for, abort, flash

@app.route("/admin/branches", methods=["GET", "POST"])
def admin_branches():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    try:
        # ===================== POST: Add new branch =====================
        if request.method == "POST":
            city = request.form.get("city", "").strip()
            address = request.form.get("address", "").strip()
            phone = request.form.get("phone", "").strip()

            if not city or not address or not phone:
                flash("All fields are required.", "error")
                return redirect(url_for("admin_branches"))

            cur.execute(
                "INSERT INTO Branch (city, address, phone) VALUES (%s, %s, %s)",
                (city, address, phone)
            )
            conn.commit()
            return redirect(url_for("admin_branches"))

        # ===================== GET: List + Search =====================
        field = request.args.get("field", "all").strip()
        search = request.args.get("search", "").strip()   # <-- مهم: نفس اسم input بالـ HTML

        params = None
        sql = "SELECT * FROM Branch"

        if search:
            if field == "city":
                sql += " WHERE city LIKE %s"
                params = (f"%{search}%",)
            elif field == "address":
                sql += " WHERE address LIKE %s"
                params = (f"%{search}%",)
            elif field == "phone":
                sql += " WHERE phone LIKE %s"
                params = (f"%{search}%",)
            else:
                sql += " WHERE city LIKE %s OR address LIKE %s OR phone LIKE %s"
                params = (f"%{search}%", f"%{search}%", f"%{search}%")

        sql += " ORDER BY branch_id DESC"

        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)

        branches = cur.fetchall()

        return render_template(
            "branches.html",
            branches=branches,
            field=field,
            search=search
        )

    finally:
        cur.close()
        conn.close()


# ===================== DELETE  =====================
@app.route("/admin/branches/delete/<int:branch_id>", methods=["POST"])
def delete_branch(branch_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    try:
        cur.execute("DELETE FROM Branch WHERE branch_id = %s", (branch_id,))
        conn.commit()
        return redirect(url_for("admin_branches"))
    finally:
        cur.close()
        conn.close()


# ===================== EDIT =====================
@app.route("/admin/branches/edit/<int:branch_id>", methods=["GET", "POST"])
def edit_branch(branch_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    try:
        if request.method == "POST":
            city = request.form.get("city", "").strip()
            address = request.form.get("address", "").strip()
            phone = request.form.get("phone", "").strip()

            if not city or not address or not phone:
                flash("All fields are required.", "error")
                return redirect(url_for("edit_branch", branch_id=branch_id))

            cur.execute("""
                UPDATE Branch
                SET city=%s, address=%s, phone=%s
                WHERE branch_id=%s
            """, (city, address, phone, branch_id))

            conn.commit()
            return redirect(url_for("admin_branches"))

        # GET: branch data
        cur.execute("SELECT * FROM Branch WHERE branch_id=%s", (branch_id,))
        branch = cur.fetchone()
        if not branch:
            abort(404)

        return render_template("edit_branch.html", branch=branch)

    finally:
        cur.close()
        conn.close()

#--------------------#
#       product
#--------------------#
# 1) List products
@app.route("/")
def home():
    return redirect(url_for("products_list"))

@app.route("/products")
def products_list():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM product ORDER BY product_id DESC")
    products = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("products_list.html", products=products)
@app.route("/products/add", methods=["GET"])
def add_product_form():
    return render_template("product_form.html", mode="add", product=None)
@app.route("/products/add", methods=["POST"])
def add_product():
    product_name = request.form["product_name"]
    category = request.form["category"]
    brand = request.form["brand"]
    unit_price_sell = request.form["unit_price_sell"]
    unit_price_cost = request.form["unit_price_cost"]
    expiry_date = request.form["expiry_date"]
    image = request.files.get("image")
    image_name = None
    if image and image.filename != "":
        image_name = secure_filename(image.filename)
        image.save(os.path.join(UPLOAD_FOLDER, image_name))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO product
        (product_name, category, brand, unit_price_sell, unit_price_cost, expiry_date, image)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (product_name, category, brand, unit_price_sell, unit_price_cost, expiry_date, image_name))
    product_id = cur.lastrowid  

   
    warehouse_id = 4
    quantity = 6     
    cur.execute("""
        INSERT INTO warehousestock
        (warehouse_id, product_id, quantity_available, last_restock_date)
        VALUES (%s, %s, %s, CURDATE())
    """, (warehouse_id, product_id, quantity))

    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("products_list"))

@app.route("/products/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        product_name = request.form["product_name"]
        category = request.form["category"]
        brand = request.form["brand"]
        unit_price_sell = request.form["unit_price_sell"]
        unit_price_cost = request.form["unit_price_cost"]
        expiry_date = request.form["expiry_date"]

        image = request.files.get("image")
        image_name = request.form.get("old_image")

        if image and image.filename != "":
            image_name = secure_filename(image.filename)
            image.save(os.path.join(UPLOAD_FOLDER, image_name))

        cur.execute("""
            UPDATE product
            SET product_name=%s, category=%s, brand=%s,
                unit_price_sell=%s, unit_price_cost=%s,
                expiry_date=%s, image=%s
            WHERE product_id=%s
        """, (
            product_name, category, brand,
            unit_price_sell, unit_price_cost,
            expiry_date, image_name, product_id
        ))

        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("products_list"))

    # GET
    cur.execute("SELECT * FROM product WHERE product_id=%s", (product_id,))
    product = cur.fetchone()
    cur.close()
    conn.close()

    return render_template("product_form.html", mode="edit", product=product)


# 6) Delete product
@app.route("/products/delete/<int:product_id>")
def delete_product(product_id):
    conn = get_db_connection()
    cur = conn.cursor()

    # warehousestock
    cur.execute("DELETE FROM warehousestock WHERE product_id = %s", (product_id,))

    cur.execute("DELETE FROM product WHERE product_id = %s", (product_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("products_list"))
#---------------------------#
#         suppliers
#---------------------------#
@app.route('/suppliers')
def suppliers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM supplier")
    suppliers = cursor.fetchall()
    conn.close()
    return render_template('suppliers/suppliers_list.html', suppliers=suppliers)

@app.route('/supplier/add', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        name = request.form['supplier_name']
        phone = request.form['phone']
        country = request.form['country']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO supplier (supplier_name, phone, country) VALUES (%s, %s, %s)",
            (name, phone, country)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('suppliers'))

    return render_template('suppliers/add_supplier.html')

@app.route('/supplier/delete/<int:id>')
def delete_supplier(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM supplier WHERE supplier_id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('suppliers'))
@app.route('/supplier/edit/<int:id>', methods=['GET', 'POST'])
def edit_supplier(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['supplier_name']
        phone = request.form['phone']
        country = request.form['country']

        cursor.execute("""
            UPDATE supplier
            SET supplier_name=%s, phone=%s, country=%s
            WHERE supplier_id=%s
        """, (name, phone, country, id))

        conn.commit()
        conn.close()
        return redirect(url_for('suppliers'))

    cursor.execute("SELECT * FROM supplier WHERE supplier_id=%s", (id,))
    supplier = cursor.fetchone()
    conn.close()

    return render_template('suppliers/edit_supplier.html', supplier=supplier)
#-----------------------------------#
#        warehouses
#-----------------------------------# 
@app.route('/admin/warehouses')
def admin_warehouses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT w.warehouse_id, w.warehouse_name, w.location, w.phone,
               b.city AS branch_city
        FROM warehouse w
        JOIN branch b ON w.branch_id = b.branch_id
    """)
    warehouses = cursor.fetchall()

    conn.close()
    return render_template(
        '/warehouses_list.html',
        warehouses=warehouses
    )
@app.route('/admin/warehouses/add', methods=['GET', 'POST'])
def add_warehouse():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        cursor.execute("""
            INSERT INTO warehouse (warehouse_name, location, phone, branch_id)
            VALUES (%s, %s, %s, %s)
        """, (
            request.form['warehouse_name'],
            request.form['location'],
            request.form['phone'],
            request.form['branch_id']
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_warehouses'))

    cursor.execute("SELECT branch_id, city FROM branch")
    branches = cursor.fetchall()
    conn.close()

    return render_template('add_warehouse.html', branches=branches)


@app.route('/admin/warehouses/edit/<int:id>', methods=['GET', 'POST'])
def edit_warehouse(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM branch")
    branches = cursor.fetchall()

    if request.method == 'POST':
        cursor.execute("""
            UPDATE warehouse
            SET warehouse_name=%s, location=%s, phone=%s, branch_id=%s
            WHERE warehouse_id=%s
        """, (
            request.form['warehouse_name'],
            request.form['location'],
            request.form['phone'],
            request.form['branch_id'],
            id
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_warehouses'))

    cursor.execute("SELECT * FROM warehouse WHERE warehouse_id=%s", (id,))
    warehouse = cursor.fetchone()
    conn.close()

    return render_template(
        '/edit_warehouse.html',
        warehouse=warehouse,
        branches=branches
    )
@app.route('/admin/warehouses/delete/<int:id>')
def delete_warehouse(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM warehouse WHERE warehouse_id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_warehouses'))
#-----------------------------------#
#          employee
#-----------------------------------#
@app.route('/admin/employees')
def admin_employees():
    search = request.args.get('search', '')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT 
        e.employee_id,
        e.name,
        e.position,
        e.salary,
        b.city AS branch_name,
        w.warehouse_name AS warehouse_name
    FROM Employee e
    JOIN Branch b ON e.branch_id = b.branch_id
    LEFT JOIN Warehouse w ON e.warehouse_id = w.warehouse_id
    WHERE e.name LIKE %s
    """

    cursor.execute(query, (f"%{search}%",))
    employees = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) AS total FROM Employee")
    total = cursor.fetchone()['total']

    conn.close()

    return render_template(
        'employees_list.html',
        employees=employees,
        total=total,
        search=search
    )

@app.route('/admin/employees/add', methods=['GET', 'POST'])
def add_employee():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        cursor.execute("""
            INSERT INTO Employee (name, position, salary, branch_id, warehouse_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            request.form['name'],
            request.form['position'],
            request.form['salary'],
            request.form['branch_id'],
            request.form.get('warehouse_id') or None
        ))
        conn.commit()
        conn.close()
        return redirect('/admin/employees')

    cursor.execute("SELECT branch_id, city FROM Branch")
    branches = cursor.fetchall()

    cursor.execute("SELECT warehouse_id, warehouse_name FROM Warehouse")
    warehouses = cursor.fetchall()

    conn.close()
    return render_template(
        'add_employee.html',
        branches=branches,
        warehouses=warehouses
    )
@app.route('/admin/employees/delete/<int:id>')
def delete_employee(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Employee WHERE employee_id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect('/admin/employees')
@app.route('/admin/employees/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        cursor.execute("""
            UPDATE Employee
            SET name=%s, position=%s, salary=%s, branch_id=%s, warehouse_id=%s
            WHERE employee_id=%s
        """, (
            request.form['name'],
            request.form['position'],
            request.form['salary'],
            request.form['branch_id'],
            request.form.get('warehouse_id') or None,
            id
        ))
        conn.commit()
        conn.close()
        return redirect('/admin/employees')

    # GET
    cursor.execute("SELECT * FROM Employee WHERE employee_id=%s", (id,))
    employee = cursor.fetchone()

    cursor.execute("SELECT branch_id, city FROM Branch")
    branches = cursor.fetchall()

    cursor.execute("SELECT warehouse_id, warehouse_name FROM Warehouse")
    warehouses = cursor.fetchall()

    conn.close()

    return render_template(
        'edit_employee.html',
        employee=employee,
        branches=branches,
        warehouses=warehouses
    )
#-----------------------------------#
#        customer
#-------------------------------------#
from werkzeug.security import generate_password_hash

from flask import request, render_template, redirect, url_for, session, abort, flash
from werkzeug.security import generate_password_hash

@app.route("/admin/customers", methods=["GET", "POST"])
def admin_customers():
    # Auth
    if "role" not in session or session["role"] != "admin":
        return redirect(url_for("login_admin"))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    try:
        # ---------- ADD (POST) ----------
        if request.method == "POST":
            customer_name = request.form.get("customer_name", "").strip()
            ctype = request.form.get("type", "").strip()
            city = request.form.get("city", "").strip()
            phone = request.form.get("phone", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "").strip()

            if not all([customer_name, ctype, city, phone, email, password]):
                flash("All fields are required.", "error")
                return redirect(url_for("admin_customers"))

            pw_hash = generate_password_hash(password)

            cur.execute("""
                INSERT INTO Customer (customer_name, type, city, phone, email, password_hash)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (customer_name, ctype, city, phone, email, pw_hash))
            conn.commit()

            return redirect(url_for("admin_customers"))

        # ---------- SEARCH (GET) ----------
        field = request.args.get("field", "all").strip()
        search = request.args.get("search", "").strip()   # <-- بدل q عشان يطابق الـ HTML

        sql = "SELECT customer_id, customer_name, type, city, phone, email FROM Customer"
        params = None

        if search:
            if field == "name":
                sql += " WHERE customer_name LIKE %s"
                params = (f"%{search}%",)
            elif field == "type":
                sql += " WHERE type LIKE %s"
                params = (f"%{search}%",)
            elif field == "city":
                sql += " WHERE city LIKE %s"
                params = (f"%{search}%",)
            elif field == "phone":
                sql += " WHERE phone LIKE %s"
                params = (f"%{search}%",)
            elif field == "email":
                sql += " WHERE email LIKE %s"
                params = (f"%{search}%",)
            else:
                sql += """ WHERE customer_name LIKE %s OR type LIKE %s OR city LIKE %s
                           OR phone LIKE %s OR email LIKE %s """
                params = (f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%")

        sql += " ORDER BY customer_id DESC"

        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)

        customers = cur.fetchall()

        return render_template(
            "customers.html",
            title="Customers",
            customers=customers,
            field=field,
            search=search
        )

    finally:
        cur.close()
        conn.close()


@app.route("/admin/customers/edit/<int:customer_id>", methods=["GET", "POST"])
def edit_customer(customer_id):
    if "role" not in session or session["role"] != "admin":
        return redirect(url_for("login_admin"))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    try:
        if request.method == "POST":
            customer_name = request.form.get("customer_name", "").strip()
            ctype = request.form.get("type", "").strip()
            city = request.form.get("city", "").strip()
            phone = request.form.get("phone", "").strip()
            email = request.form.get("email", "").strip()
            new_password = request.form.get("password", "").strip()

            if not all([customer_name, ctype, city, phone, email]):
                flash("Please fill all required fields.", "error")
                return redirect(url_for("edit_customer", customer_id=customer_id))

            if new_password:
                pw_hash = generate_password_hash(new_password)
                cur.execute("""
                    UPDATE Customer
                    SET customer_name=%s, type=%s, city=%s, phone=%s, email=%s, password_hash=%s
                    WHERE customer_id=%s
                """, (customer_name, ctype, city, phone, email, pw_hash, customer_id))
            else:
                cur.execute("""
                    UPDATE Customer
                    SET customer_name=%s, type=%s, city=%s, phone=%s, email=%s
                    WHERE customer_id=%s
                """, (customer_name, ctype, city, phone, email, customer_id))

            conn.commit()
            return redirect(url_for("admin_customers"))

        # GET
        cur.execute("SELECT * FROM Customer WHERE customer_id=%s", (customer_id,))
        customer = cur.fetchone()
        if not customer:
            abort(404)

        return render_template("edit_customer.html", customer=customer, title="Edit Customer")

    finally:
        cur.close()
        conn.close()



@app.route("/admin/customers/delete/<int:customer_id>", methods=["POST"])
def delete_customer(customer_id):
    if "role" not in session or session["role"] != "admin":
        return redirect(url_for("login_admin"))

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM Customer WHERE customer_id=%s", (customer_id,))
        conn.commit()
        return redirect(url_for("admin_customers"))
    finally:
        cur.close()
        conn.close()
#-----------------------------------#
#        stock
#-----------------------------------# 
@app.route("/admin/stock", methods=["GET"])
def admin_stock():
    if "role" not in session or session["role"] != "admin":
        return redirect(url_for("login_admin"))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    try:
        field = request.args.get("field", "all").strip()
        search = request.args.get("search", "").strip()

        sql = """
            SELECT
              ws.warehouse_id,
              ws.product_id,
              w.warehouse_name,
              p.product_name,
              ws.quantity_available,
              ws.last_restock_date
            FROM warehousestock ws
            JOIN warehouse w ON w.warehouse_id = ws.warehouse_id
            JOIN product p   ON p.product_id   = ws.product_id
        """
        params = None

        if search:
            if field == "warehouse":
                sql += " WHERE w.warehouse_name LIKE %s"
                params = (f"%{search}%",)
            elif field == "product":
                sql += " WHERE p.product_name LIKE %s"
                params = (f"%{search}%",)
            else:
                sql += " WHERE w.warehouse_name LIKE %s OR p.product_name LIKE %s"
                params = (f"%{search}%", f"%{search}%")

        sql += " ORDER BY w.warehouse_name, p.product_name"

        cur.execute(sql, params) if params else cur.execute(sql)
        items = cur.fetchall()

        return render_template(
            "warehouse_stock.html",
            items=items,
            field=field,
            search=search
        )
    finally:
        cur.close()
        conn.close()
@app.route("/admin/stock/update/<int:warehouse_id>/<int:product_id>", methods=["GET", "POST"])
def update_stock(warehouse_id, product_id):
    if "role" not in session or session["role"] != "admin":
        return redirect(url_for("login_admin"))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    try:
        if request.method == "POST":
            new_qty = request.form.get("quantity_available", "").strip()
            restock_date = request.form.get("last_restock_date", "").strip()  # optional

            if not new_qty.isdigit():
                flash("Quantity must be a valid number.", "error")
                return redirect(url_for("update_stock", warehouse_id=warehouse_id, product_id=product_id))

            new_qty = int(new_qty)

            # إذا المستخدم ما دخل تاريخ: خليها CURDATE()
            if restock_date:
                cur.execute("""
                    UPDATE warehousestock
                    SET quantity_available=%s, last_restock_date=%s
                    WHERE warehouse_id=%s AND product_id=%s
                """, (new_qty, restock_date, warehouse_id, product_id))
            else:
                cur.execute("""
                    UPDATE warehousestock
                    SET quantity_available=%s, last_restock_date=CURDATE()
                    WHERE warehouse_id=%s AND product_id=%s
                """, (new_qty, warehouse_id, product_id))

            conn.commit()
            flash("Stock updated successfully.", "success")
            return redirect(url_for("admin_stock"))

        # GET: bring current record
        cur.execute("""
            SELECT
              ws.warehouse_id, ws.product_id,
              w.warehouse_name,
              p.product_name,
              ws.quantity_available,
              ws.last_restock_date
            FROM warehousestock ws
            JOIN warehouse w ON w.warehouse_id = ws.warehouse_id
            JOIN product p   ON p.product_id   = ws.product_id
            WHERE ws.warehouse_id=%s AND ws.product_id=%s
        """, (warehouse_id, product_id))
        item = cur.fetchone()

        if not item:
            flash("Stock record not found.", "error")
            return redirect(url_for("admin_stock"))

        return render_template("update_stock.html", item=item)

    finally:
        cur.close()
        conn.close()
#-----------------------------------#
#        purchase_orders
#-----------------------------------# 
@app.route('/purchase_orders')
def purchase_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT po.po_id, po.order_date, po.total_cost,
               s.supplier_name
        FROM purchaseorder po
        JOIN supplier s ON po.supplier_id = s.supplier_id
    """)
    orders = cursor.fetchall()
    conn.close()

    return render_template('purchase/purchase_orders.html', orders=orders)

@app.route('/purchase_order/add', methods=['GET', 'POST'])
def add_purchase_order():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM supplier")
    suppliers = cursor.fetchall()

    if request.method == 'POST':
        supplier_id = request.form['supplier_id']

        cursor2 = conn.cursor()
        cursor2.execute(
            "INSERT INTO purchaseorder (supplier_id, order_date, total_cost) VALUES (%s, CURDATE(), 0)",
            (supplier_id,)
        )
        conn.commit()
        po_id = cursor2.lastrowid
        conn.close()

        return redirect(url_for('purchase_order_details', id=po_id))

    conn.close()
    return render_template('purchase/add_purchase_order.html', suppliers=suppliers)

@app.route('/purchase_order/<int:id>')
def purchase_order_details(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT po.po_id, po.order_date, po.total_cost,
               s.supplier_name
        FROM purchaseorder po
        JOIN supplier s ON po.supplier_id = s.supplier_id
        WHERE po.po_id = %s
    """, (id,))
    order = cursor.fetchone()

    cursor.execute("""
        SELECT poi.*, p.product_name, w.warehouse_name
        FROM purchaseorderitem poi
        JOIN product p ON poi.product_id = p.product_id
        JOIN warehouse w ON poi.warehouse_id = w.warehouse_id
        WHERE poi.po_id = %s
    """, (id,))
    items = cursor.fetchall()

    cursor.execute("SELECT * FROM product")
    products = cursor.fetchall()

    cursor.execute("SELECT * FROM warehouse")
    warehouses = cursor.fetchall()

    conn.close()

    return render_template(
        'purchase/purchase_order_details.html',
        order=order,
        items=items,
        products=products,
        warehouses=warehouses
    )

@app.route('/purchase_order/delete/<int:id>')
def delete_purchase_order(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM purchaseorder WHERE po_id=%s", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('purchase_orders'))

@app.route('/purchase_order/item/add', methods=['POST'])
def add_purchase_order_item():
    po_id = request.form['po_id']
    product_id = request.form['product_id']
    warehouse_id = request.form['warehouse_id']
    qty = request.form['qty']
    cost = request.form['cost']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Add item
    cursor.execute("""
        INSERT INTO purchaseorderitem
        (po_id, product_id, warehouse_id, qty_received, cost_per_unit)
        VALUES (%s, %s, %s, %s, %s)
    """, (po_id, product_id, warehouse_id, qty, cost))

    # Update stock
    cursor.execute("""
        INSERT INTO warehousestock
        (warehouse_id, product_id, quantity_available, last_restock_date)
        VALUES (%s, %s, %s, CURDATE())
        ON DUPLICATE KEY UPDATE
        quantity_available = quantity_available + %s,
        last_restock_date = CURDATE()
    """, (warehouse_id, product_id, qty, qty))

    # Update total cost
    cursor.execute("""
        UPDATE purchaseorder
        SET total_cost = (
            SELECT SUM(qty_received * cost_per_unit)
            FROM purchaseorderitem
            WHERE po_id = %s
        )
        WHERE po_id = %s
    """, (po_id, po_id))

    conn.commit()
    conn.close()

    return redirect(url_for('purchase_order_details', id=po_id))

@app.route('/reports/purchases_by_supplier')
def purchases_by_supplier():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.supplier_name,
               SUM(poi.qty_received * poi.cost_per_unit) AS total
        FROM purchaseorder po
        JOIN supplier s ON po.supplier_id = s.supplier_id
        JOIN purchaseorderitem poi ON po.po_id = poi.po_id
        GROUP BY s.supplier_name
    """)

    data = cursor.fetchall()
    conn.close()

    return render_template('reports/purchases_by_supplier.html', data=data)

@app.route('/reports/inventory_value')
def inventory_value():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT w.warehouse_name,
               SUM(ws.quantity_available * p.unit_price_cost) AS value
        FROM warehousestock ws
        JOIN warehouse w ON ws.warehouse_id = w.warehouse_id
        JOIN product p ON ws.product_id = p.product_id
        GROUP BY w.warehouse_name
    """)

    data = cursor.fetchall()
    conn.close()

    return render_template('reports/inventory_value.html', data=data)
#-----------------------------------#
#        sales_orders
#-----------------------------------#
@app.route('/sales_orders')
def sales_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT so.so_id, so.sales_date, so.total_amount,
               c.customer_name, b.city AS branch_city
        FROM salesorder so
        JOIN customer c ON so.customer_id = c.customer_id
        JOIN Branch b ON so.branch_id = b.branch_id
        ORDER BY so.so_id DESC
    """)
    orders = cursor.fetchall()
    conn.close()

    return render_template('sales/sales_orders.html', orders=orders)


@app.route('/sales_order/add', methods=['GET', 'POST'])
def add_sales_order():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT customer_id, customer_name FROM customer")
    customers = cursor.fetchall()

    cursor.execute("SELECT branch_id, city FROM Branch")  # ✅ Branch not branch
    branches = cursor.fetchall()

    if request.method == 'POST':
        customer_id = request.form['customer_id']
        branch_id = request.form['branch_id']

        cursor2 = conn.cursor()
        cursor2.execute("""
            INSERT INTO salesorder
            (customer_id, branch_id, sales_date, total_amount, payment_status)
            VALUES (%s, %s, CURDATE(), 0, 'Pending')
        """, (customer_id, branch_id))

        conn.commit()
        so_id = cursor2.lastrowid
        conn.close()

        return redirect(url_for('sales_order_details', id=so_id))

    conn.close()
    return render_template(
        'sales/add_sales_order.html',
        customers=customers,
        branches=branches
    )


@app.route('/sales_order/<int:id>')
def sales_order_details(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Order header
    cursor.execute("""
        SELECT so.so_id, so.sales_date, so.total_amount, so.payment_status,
               c.customer_name, b.city AS branch_city
        FROM salesorder so
        JOIN customer c ON so.customer_id = c.customer_id
        JOIN Branch b ON so.branch_id = b.branch_id
        WHERE so.so_id = %s
    """, (id,))
    order = cursor.fetchone()

    if not order:
        conn.close()
        flash("Order not found.", "danger")
        return redirect(url_for("sales_orders"))

    # Items (includes warehouse + LEFT JOIN to avoid hiding rows if warehouse_id is NULL)
    cursor.execute("""
        SELECT
          soi.product_id,
          p.product_name,
          soi.warehouse_id,
          w.warehouse_name,
          soi.qty_sold,
          soi.selling_price_per_unit
        FROM SalesOrderItem soi
        JOIN product p ON p.product_id = soi.product_id
        LEFT JOIN Warehouse w ON w.warehouse_id = soi.warehouse_id
        WHERE soi.so_id = %s
        ORDER BY p.product_name
    """, (id,))
    items = cursor.fetchall()

    # Dropdowns for add item
    cursor.execute("SELECT product_id, product_name FROM product ORDER BY product_name")
    products = cursor.fetchall()

    cursor.execute("SELECT warehouse_id, warehouse_name FROM Warehouse ORDER BY warehouse_name")
    warehouses = cursor.fetchall()

    conn.close()

    return render_template(
        'sales/sales_order_details.html',
        order=order,
        items=items,
        products=products,
        warehouses=warehouses
    )


@app.route('/sales_order/item/add', methods=['POST'])
def add_sales_order_item():
    so_id = int(request.form['so_id'])
    product_id = int(request.form['product_id'])
    warehouse_id = int(request.form['warehouse_id'])
    qty = int(request.form['qty'])
    price = float(request.form['price'])

    if qty <= 0 or price < 0:
        flash("Invalid quantity or price.", "danger")
        return redirect(url_for('sales_order_details', id=so_id))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    try:
        # Check stock availability
        cur.execute("""
            SELECT quantity_available
            FROM warehousestock
            WHERE warehouse_id=%s AND product_id=%s
        """, (warehouse_id, product_id))
        stock = cur.fetchone()

        if not stock or int(stock["quantity_available"]) < qty:
            flash("Not enough stock in this warehouse.", "danger")
            return redirect(url_for('sales_order_details', id=so_id))

        cur2 = conn.cursor()

        # Insert item ( correct column names)
        cur2.execute("""
            INSERT INTO salesorderitem
            (so_id, product_id, warehouse_id, qty_sold, selling_price_per_unit)
            VALUES (%s, %s, %s, %s, %s)
        """, (so_id, product_id, warehouse_id, qty, price))

        # Reduce stock
        cur2.execute("""
            UPDATE warehousestock
            SET quantity_available = quantity_available - %s
            WHERE warehouse_id = %s AND product_id = %s
        """, (qty, warehouse_id, product_id))

        # Update total amount in salesorder
        cur2.execute("""
            UPDATE salesorder
            SET total_amount = (
                SELECT COALESCE(SUM(qty_sold * selling_price_per_unit), 0)
                FROM salesorderitem
                WHERE so_id = %s
            )
            WHERE so_id = %s
        """, (so_id, so_id))

        conn.commit()
        flash("Item added successfully.", "success")
        return redirect(url_for('sales_order_details', id=so_id))

    except Exception:
        conn.rollback()
        flash("Failed to add item.", "danger")
        return redirect(url_for('sales_order_details', id=so_id))

    finally:
        cur.close()
        conn.close()
# -----------------------------------
#     reports page 
# -----------------------------------
from functools import wraps
from flask import render_template, request, session, redirect, url_for, flash
import json, re, calendar
from datetime import datetime

# ---------- Admin guard ----------
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "danger")
            return redirect(url_for("login_admin"))

        is_admin = (session.get("role") == "admin") or (session.get("user_type") == "admin")
        if not is_admin:
            flash("Access denied. Admins only.", "danger")
            return redirect(url_for("shop"))

        return f(*args, **kwargs)
    return decorated


def safe_city(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return "Ramallah"
    # letters, spaces, dash only
    if not re.fullmatch(r"[A-Za-z\s\-]{2,40}", s):
        return "Ramallah"
    return s


def safe_month(s: str) -> str:
    s = (s or "").strip()
    if not re.fullmatch(r"\d{4}-\d{2}", s):
        now = datetime.now()
        return f"{now.year:04d}-{now.month:02d}"
    return s


@app.route("/reports")
@admin_required
def reports():
    # --------- Filters ----------
    month = safe_month(request.args.get("month"))  # YYYY-MM
    branch_city = safe_city(request.args.get("branch_city"))
    threshold = request.args.get("threshold", "10")

    try:
        threshold = int(threshold)
        if threshold < 1:
            threshold = 10
    except:
        threshold = 10

    # dropdown customer (optional)
    chosen_customer_id = request.args.get("customer_id")
    try:
        chosen_customer_id = int(chosen_customer_id) if chosen_customer_id else None
    except:
        chosen_customer_id = None

    # month range
    y, m = map(int, month.split("-"))
    start_date = f"{y:04d}-{m:02d}-01"
    last_day = calendar.monthrange(y, m)[1]
    end_date = f"{y:04d}-{m:02d}-{last_day:02d}"

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True, buffered=True)

    # ============================
    # Dropdown data (Customers list)
    # ============================
    cur.execute("""
        SELECT customer_id, customer_name
        FROM customer
        ORDER BY customer_name ASC;
    """)
    customers_list = cur.fetchall()

    # If no customer selected, pick first customer in list (safe default)
    if chosen_customer_id is None:
        chosen_customer_id = customers_list[0]["customer_id"] if customers_list else 1

    # customer name for UI
    cur.execute("SELECT customer_name FROM customer WHERE customer_id = %s", (chosen_customer_id,))
    row_name = cur.fetchone()
    chosen_customer_name = row_name["customer_name"] if row_name else f"Customer #{chosen_customer_id}"

    # ============================
    # KPIs (Sales-focused + simple)
    # ============================

    # KPI1: Total Sales Revenue (all branches, month)
    cur.execute("""
        SELECT COALESCE(SUM(total_amount), 0) AS total_sales_revenue
        FROM salesorder
        WHERE sales_date BETWEEN %s AND %s;
    """, (start_date, end_date))
    kpi_total_sales_revenue = float(cur.fetchone()["total_sales_revenue"] or 0)

    # KPI2: Total Orders in selected Branch City (month)
    cur.execute("""
        SELECT COUNT(*) AS total_orders
        FROM salesorder so
        JOIN branch b ON b.branch_id = so.branch_id
        WHERE so.sales_date BETWEEN %s AND %s
          AND b.city = %s;
    """, (start_date, end_date, branch_city))
    kpi_total_orders_branch = int(cur.fetchone()["total_orders"] or 0)

    # KPI3: Low stock count for selected Branch City
   # This KPI helps management monitor low inventory levels per branch city
    #and supports restocking decisions using a dynamic threshold
    cur.execute("""
        SELECT COUNT(*) AS low_stock_count
        FROM warehousestock ws
        JOIN warehouse w ON w.warehouse_id = ws.warehouse_id
        JOIN branch b ON b.branch_id = w.branch_id
        WHERE b.city = %s
          AND ws.quantity_available < %s;
    """, (branch_city, threshold))
    kpi_low_stock_count = int(cur.fetchone()["low_stock_count"] or 0)

    # KPI4: Computes the total inventory value across all warehouses
    # Inventory value = quantity_available × unit_price_cost (normalized schema, no data duplication)
    cur.execute("""
        SELECT COALESCE(SUM(ws.quantity_available * p.unit_price_cost), 0) AS total_inventory_value
        FROM warehousestock ws
        JOIN product p ON p.product_id = ws.product_id;
    """)
    kpi_total_inventory_value = float(cur.fetchone()["total_inventory_value"] or 0)

    kpis = {
        "total_sales_revenue": kpi_total_sales_revenue,
        "total_orders_branch": kpi_total_orders_branch,
        "low_stock_count": kpi_low_stock_count,
        "total_inventory_value": kpi_total_inventory_value
    }

    # ============================
    # TABLES (Customer-related)
    # ============================

    # Q1: Customer Orders (month + selected branch city)
    cur.execute("""
        SELECT so.so_id, c.customer_name, b.city AS branch_city,
               so.sales_date, so.total_amount, so.payment_status
        FROM salesorder so
        JOIN customer c ON so.customer_id = c.customer_id
        JOIN branch b ON so.branch_id = b.branch_id
        WHERE c.customer_id = %s
          AND so.sales_date BETWEEN %s AND %s
          AND b.city = %s
        ORDER BY so.sales_date DESC;
    """, (chosen_customer_id, start_date, end_date, branch_city))
    t_orders = cur.fetchall()

    # choose latest order for details table
    chosen_so_id = t_orders[0]["so_id"] if t_orders else None

    # Q3: Customer Order History (all time for chosen customer)
    cur.execute("""
        SELECT so.so_id, so.sales_date, so.payment_status,
               COUNT(soi.product_id) AS items_count,
               COALESCE(SUM(soi.qty_sold * soi.selling_price_per_unit), 0) AS computed_total
        FROM salesorder so
        JOIN salesorderitem soi ON so.so_id = soi.so_id
        WHERE so.customer_id = %s
        GROUP BY so.so_id, so.sales_date, so.payment_status
        ORDER BY so.sales_date DESC;
    """, (chosen_customer_id,))
    t_history = cur.fetchall()

    # Q4: Order Details (latest order) - NO category (uses brand)
    if chosen_so_id:
        cur.execute("""
            SELECT so.so_id, so.sales_date,
                   p.product_name, p.brand,
                   soi.qty_sold, soi.selling_price_per_unit,
                   (soi.qty_sold * soi.selling_price_per_unit) AS line_total
            FROM salesorder so
            JOIN salesorderitem soi ON so.so_id = soi.so_id
            JOIN product p ON p.product_id = soi.product_id
            WHERE so.so_id = %s
            ORDER BY p.brand, p.product_name;
        """, (chosen_so_id,))
        t_order_details = cur.fetchall()
    else:
        t_order_details = []

    # Optional table: Purchases details (month) - still valid and useful
    # Pick top supplier + top warehouse for this month
    cur.execute("""
        SELECT po.supplier_id, COALESCE(SUM(po.total_cost),0) AS spent
        FROM purchaseorder po
        WHERE po.order_date BETWEEN %s AND %s
        GROUP BY po.supplier_id
        ORDER BY spent DESC
        LIMIT 1;
    """, (start_date, end_date))
    row_s = cur.fetchone()
    chosen_supplier_id = int(row_s["supplier_id"]) if row_s else 1

    cur.execute("""
        SELECT poi.warehouse_id, COALESCE(SUM(poi.qty_received),0) AS qty
        FROM purchaseorderitem poi
        JOIN purchaseorder po ON po.po_id = poi.po_id
        WHERE po.order_date BETWEEN %s AND %s
        GROUP BY poi.warehouse_id
        ORDER BY qty DESC
        LIMIT 1;
    """, (start_date, end_date))
    row_w = cur.fetchone()
    chosen_warehouse_id = int(row_w["warehouse_id"]) if row_w else 1

    # Q8: Purchases details for (supplier + month + warehouse)
    cur.execute("""
        SELECT po.po_id, s.supplier_name, po.order_date,
               w.warehouse_name, p.product_name,
               poi.qty_received, poi.cost_per_unit,
               (poi.qty_received * poi.cost_per_unit) AS line_total
        FROM purchaseorder po
        JOIN supplier s ON s.supplier_id = po.supplier_id
        JOIN purchaseorderitem poi ON poi.po_id = po.po_id
        JOIN warehouse w ON w.warehouse_id = poi.warehouse_id
        JOIN product p ON p.product_id = poi.product_id
        WHERE s.supplier_id = %s
          AND po.order_date BETWEEN %s AND %s
          AND w.warehouse_id = %s
        ORDER BY po.order_date DESC;
    """, (chosen_supplier_id, start_date, end_date, chosen_warehouse_id))
    t_purchases = cur.fetchall()

    # ============================
    # CHARTS (NO category)
    # ============================

    # Chart 1 (Q6): Best-selling products per branch (Qty)
    cur.execute("""
        SELECT b.city AS branch_city, p.product_name,
               COALESCE(SUM(soi.qty_sold),0) AS total_qty,
               COALESCE(SUM(soi.qty_sold * soi.selling_price_per_unit),0) AS total_revenue
        FROM salesorder so
        JOIN branch b ON so.branch_id = b.branch_id
        JOIN salesorderitem soi ON so.so_id = soi.so_id
        JOIN product p ON p.product_id = soi.product_id
        WHERE so.sales_date BETWEEN %s AND %s
        GROUP BY b.city, p.product_name
        ORDER BY b.city, total_qty DESC;
    """, (start_date, end_date))
    q6_rows = cur.fetchall()

    # Chart 2 (Q9): Purchases by supplier (month)
    cur.execute("""
        SELECT s.supplier_name,
               COUNT(po.po_id) AS orders_count,
               COALESCE(SUM(po.total_cost),0) AS total_purchased
        FROM supplier s
        JOIN purchaseorder po ON s.supplier_id = po.supplier_id
        WHERE po.order_date BETWEEN %s AND %s
        GROUP BY s.supplier_id, s.supplier_name
        ORDER BY total_purchased DESC;
    """, (start_date, end_date))
    q9_rows = cur.fetchall()

    # Chart 3 (Q10): Most purchased products (qty received) - uses brand, no category
    cur.execute("""
        SELECT p.product_name, p.brand,
               COALESCE(SUM(poi.qty_received),0) AS total_received_qty
        FROM purchaseorderitem poi
        JOIN purchaseorder po ON po.po_id = poi.po_id
        JOIN product p ON p.product_id = poi.product_id
        WHERE po.order_date BETWEEN %s AND %s
        GROUP BY p.product_id, p.product_name, p.brand
        ORDER BY total_received_qty DESC;
    """, (start_date, end_date))
    q10_rows = cur.fetchall()

    # Chart 4 (Q12): Warehouse stock summary (total units)
    cur.execute("""
        SELECT w.warehouse_name,
               COUNT(ws.product_id) AS products_count,
               COALESCE(SUM(ws.quantity_available),0) AS total_units
        FROM warehouse w
        JOIN warehousestock ws ON ws.warehouse_id = w.warehouse_id
        GROUP BY w.warehouse_id, w.warehouse_name
        ORDER BY total_units DESC;
    """)
    q12_rows = cur.fetchall()

    cur.close()
    conn.close()

    # ---- chart preparation for multi-branch dataset ----
    top_products = {}
    branches = set()
    for r in q6_rows:
        branches.add(r["branch_city"])
        pname = r["product_name"]
        top_products[pname] = top_products.get(pname, 0) + float(r["total_revenue"] or 0)

    top_product_names = [k for k, _ in sorted(top_products.items(), key=lambda x: x[1], reverse=True)[:6]]
    branch_list = sorted(list(branches))

    best_selling_datasets = []
    for br in branch_list:
        vals = []
        for pn in top_product_names:
            match = next((x for x in q6_rows if x["branch_city"] == br and x["product_name"] == pn), None)
            vals.append(int(match["total_qty"]) if match else 0)
        best_selling_datasets.append({"label": br, "values": vals})

    charts = {
        "best_selling_per_branch": {"labels": top_product_names, "datasets": best_selling_datasets},
        "purchases_by_supplier": {
            "labels": [r["supplier_name"] for r in q9_rows],
            "values": [float(r["total_purchased"] or 0) for r in q9_rows]
        },
        "most_purchased_products": {
            "labels": [f'{r["product_name"]}' for r in q10_rows[:10]],
            "values": [float(r["total_received_qty"] or 0) for r in q10_rows[:10]]
        },
        "warehouse_total_units": {
            "labels": [r["warehouse_name"] for r in q12_rows],
            "values": [float(r["total_units"] or 0) for r in q12_rows]
        }
    }

    return render_template(
        "reports.html",
        title="Reports",
        month=month,
        start_date=start_date,
        end_date=end_date,
        branch_city=branch_city,
        threshold=threshold,

        customers_list=customers_list,          
        chosen_customer_id=chosen_customer_id,
        chosen_customer_name=chosen_customer_name,
        chosen_so_id=chosen_so_id,
        chosen_supplier_id=chosen_supplier_id,
        chosen_warehouse_id=chosen_warehouse_id,

        kpis=kpis,
        t_orders=t_orders,
        t_history=t_history,
        t_order_details=t_order_details,
        t_purchases=t_purchases,

        charts_json=json.dumps(charts)
    )

if __name__ == '__main__':
    app.run(debug=True)
