from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "7aloshik_secret_2024"

# ─── Mock Database ──────────────────────────────────────────────────────────────

USERS = {
    "mohsen": {"id": 57, "password": "helloworld", "name": "Mohsen Ahmed", "phone": "01012345678"},
    "tips":   {"id": 34, "password": "tipsman",    "name": "Tips User",    "phone": "01098765432"},
}

MENU_ITEMS = [
    {"id": 1, "name": "Koshari Special",      "price": 45,  "category": "Egyptian Classics", "emoji": "🍲", "desc": "Rice, lentils, pasta & crispy onions"},
    {"id": 2, "name": "Hawawshi Crispy",      "price": 65,  "category": "Egyptian Classics", "emoji": "🥙", "desc": "Spiced minced meat in crispy bread"},
    {"id": 3, "name": "Ful Medames Bowl",     "price": 35,  "category": "Egyptian Classics", "emoji": "🫘", "desc": "Slow-cooked fava beans with olive oil"},
    {"id": 4, "name": "Feteer Meshaltet",     "price": 80,  "category": "Bakery",            "emoji": "🥐", "desc": "Flaky layered pastry with honey"},
    {"id": 5, "name": "Mahshi Koronb",        "price": 70,  "category": "Egyptian Classics", "emoji": "🥬", "desc": "Stuffed cabbage leaves with rice & herbs"},
    {"id": 6, "name": "Shawarma Baladi",      "price": 75,  "category": "Street Food",       "emoji": "🌯", "desc": "Egyptian-style chicken shawarma"},
    {"id": 7, "name": "Basbousa",             "price": 30,  "category": "Sweets",            "emoji": "🍮", "desc": "Semolina cake soaked in rose syrup"},
    {"id": 8, "name": "Om Ali",               "price": 55,  "category": "Sweets",            "emoji": "🍞", "desc": "Classic Egyptian bread pudding"},
    {"id": 9, "name": "Karkade Drink",        "price": 20,  "category": "Drinks",            "emoji": "🍵", "desc": "Chilled hibiscus flower drink"},
    {"id": 10,"name": "Tamiya Plate",         "price": 40,  "category": "Street Food",       "emoji": "🧆", "desc": "Egyptian falafel with salad & tahini"},
]

# Pre-seeded orders for mohsen (user_id=57) — this is what the attacker wants to see
ORDERS = [
    {
        "id": 1001,
        "user_id": 57,
        "username": "mohsen",
        "status": "Delivered",
        "total": 160,
        "created_at": "2024-11-01 14:32",
        "address": "15 Sharia Tahrir, Cairo",
        "items": [
            {"name": "Koshari Special", "qty": 2, "price": 45},
            {"name": "Karkade Drink",   "qty": 2, "price": 20},
        ]
    },
    {
        "id": 1002,
        "user_id": 57,
        "username": "mohsen",
        "status": "Delivered",
        "total": 145,
        "created_at": "2024-11-05 19:10",
        "address": "15 Sharia Tahrir, Cairo",
        "items": [
            {"name": "Hawawshi Crispy", "qty": 1, "price": 65},
            {"name": "Basbousa",        "qty": 1, "price": 30},
            {"name": "Karkade Drink",   "qty": 2, "price": 20},
        ]
    },
    {
        "id": 1003,
        "user_id": 57,
        "username": "mohsen",
        "status": "In Kitchen",
        "total": 195,
        "created_at": "2024-11-10 20:45",
        "address": "15 Sharia Tahrir, Cairo",
        "items": [
            {"name": "Feteer Meshaltet", "qty": 1, "price": 80},
            {"name": "Om Ali",           "qty": 1, "price": 55},
            {"name": "Tamiya Plate",     "qty": 1, "price": 40},
            {"name": "Karkade Drink",    "qty": 1, "price": 20},
        ]
    },
    {
        "id": 2001,
        "user_id": 34,
        "username": "tips",
        "status": "Delivered",
        "total": 110,
        "created_at": "2024-11-08 13:00",
        "address": "42 Corniche El Nile, Giza",
        "items": [
            {"name": "Shawarma Baladi", "qty": 1, "price": 75},
            {"name": "Basbousa",        "qty": 1, "price": 30},
        ]
    },
    {
        "id": 2002,
        "user_id": 34,
        "username": "tips",
        "status": "On the Way",
        "total": 75,
        "created_at": "2024-11-10 18:30",
        "address": "42 Corniche El Nile, Giza",
        "items": [
            {"name": "Ful Medames Bowl", "qty": 1, "price": 35},
            {"name": "Tamiya Plate",     "qty": 1, "price": 40},
        ]
    },
]

NEXT_ORDER_ID = 3000  # new orders start here

# ─── Auth helpers ────────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ─── Routes ──────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("home"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        user = USERS.get(username)
        if user and user["password"] == password:
            session["username"] = username
            session["user_id"]  = user["id"]
            session["name"]     = user["name"]
            return redirect(url_for("home"))
        error = "Invalid username or password."
    return render_template("login.html", error=error)

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/home")
@login_required
def home():
    return render_template("home.html",
                           menu=MENU_ITEMS,
                           username=session["username"],
                           name=session["name"])

@app.route("/cart")
@login_required
def cart():
    return render_template("cart.html",
                           username=session["username"],
                           name=session["name"])

# ─── API: Add to cart (leaks X-User-ID header in response) ───────────────────────
@app.route("/api/cart/add", methods=["POST"])
@login_required
def api_cart_add():
    data = request.get_json()
    item_id = data.get("item_id")
    item = next((i for i in MENU_ITEMS if i["id"] == item_id), None)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    user_id = session["user_id"]

    # ⚠️  VULNERABLE: The server echoes back X-User-ID in the response header.
    #     An attacker can grab this from any add-to-cart response and reuse it
    #     in the /api/orders endpoint to access another user's order history.
    response = jsonify({
        "message": f"'{item['name']}' added to your cart!",
        "item": item,
        "cart_user": session["username"]
    })
    response.headers["X-User-ID"] = str(user_id)   # <-- the vulnerable header
    return response

# ─── API: Place order ─────────────────────────────────────────────────────────────
@app.route("/api/orders/place", methods=["POST"])
@login_required
def api_place_order():
    global NEXT_ORDER_ID
    data  = request.get_json()
    cart  = data.get("cart", [])
    addr  = data.get("address", "")

    if not cart:
        return jsonify({"error": "Cart is empty"}), 400

    total = sum(i["price"] * i["qty"] for i in cart)
    order = {
        "id":         NEXT_ORDER_ID,
        "user_id":    session["user_id"],
        "username":   session["username"],
        "status":     "Received",
        "total":      total,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "address":    addr,
        "items":      cart,
    }
    ORDERS.append(order)
    NEXT_ORDER_ID += 1

    response = jsonify({"message": "Order placed successfully!", "order_id": order["id"]})
    response.headers["X-User-ID"] = str(session["user_id"])
    return response

# ─── API: Get order history ───────────────────────────────────────────────────────
# ⚠️  VULNERABLE ENDPOINT: Trusts X-User-ID header instead of session.
#     Anyone who knows (or finds) a valid user_id can fetch that user's orders.
@app.route("/api/orders", methods=["GET"])
@login_required
def api_get_orders():
    # The vulnerability: read user_id from the header if present, else fall back to session
    header_uid = request.headers.get("X-User-ID")
    if header_uid:
        try:
            user_id = int(header_uid)   # ⚠️ trusts user-supplied header!
        except ValueError:
            user_id = session["user_id"]
    else:
        user_id = session["user_id"]

    user_orders = [o for o in ORDERS if o["user_id"] == user_id]
    return jsonify({"orders": user_orders, "resolved_user_id": user_id})

@app.route("/orders")
@login_required
def orders_page():
    return render_template("orders.html",
                           username=session["username"],
                           name=session["name"])

if __name__ == "__main__":
    app.run(debug=True, port=5001)
