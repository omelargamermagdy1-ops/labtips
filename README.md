# 🥙 7aloshik — حلو شيك
### Cairo's Finest Food Delivery · Web Security Lab

---

## Running the App

```bash
pip install -r requirements.txt
python app.py
# → http://127.0.0.1:5000
```

---

## Demo Accounts

| Username | Password   |
|----------|------------|
| mohsen   | helloworld |
| tips     | tipsman    |

---

## 🔐 Vulnerability: IDOR via Trusted `X-User-ID` Header

### What's the bug?

The `/api/orders` endpoint **trusts the `X-User-ID` header** supplied by the client
instead of always using the authenticated session's user ID.

```python
# app.py — /api/orders
header_uid = request.headers.get("X-User-ID")
if header_uid:
    user_id = int(header_uid)   # ⚠️ user-controlled!
else:
    user_id = session["user_id"]
```

Meanwhile, every response from `/api/cart/add` **leaks the logged-in user's ID**
in the `X-User-ID` response header.

---

## 🧪 Exploitation Steps (IDOR Lab)

**Goal:** Log in as `tips` and read all of `mohsen`'s order history.

### Step 1 — Login as `tips`
Go to `http://127.0.0.1:5000/login` and log in with `tips / tipsman`.

### Step 2 — Find `mohsen`'s `X-User-ID`

You need to observe another user's add-to-cart response.
In a real scenario this could be via a shared/intercepted session,
but for the lab: open **DevTools → Network** and add any item to cart.

Notice the response header:
```
X-User-ID: 2        ← this is tips' own ID
```

Now we know `tips` = user_id **2**.  
Since IDs are sequential, `mohsen` = user_id **1**.

Alternatively, intercept a request while logged in as mohsen to confirm:
```
X-User-ID: 1
```

### Step 3 — Access mohsen's Orders (as tips)

While logged in as `tips`, open the browser console or Burp Suite and run:

```javascript
// In browser DevTools console (while logged in as tips):
fetch('/api/orders', {
  headers: { 'X-User-ID': '1' }   // ← inject mohsen's user ID
})
.then(r => r.json())
.then(data => console.log(JSON.stringify(data, null, 2)));
```

**Result:** You receive all of `mohsen`'s private order history — addresses,
items, totals, timestamps — without knowing his password.

---

## 🛡️ Fix

Never trust client-supplied identity headers. Always derive the user ID
from the **server-side session** only:

```python
# FIXED version:
@app.route("/api/orders")
@login_required
def api_get_orders():
    user_id = session["user_id"]   # always from session, never from headers
    user_orders = [o for o in ORDERS if o["user_id"] == user_id]
    return jsonify({"orders": user_orders})
```

Also remove the `X-User-ID` header from all API responses.

---

## File Structure

```
7aloshik/
├── app.py                  # Flask app + vulnerable endpoints
├── requirements.txt
├── templates/
│   ├── login.html
│   ├── navbar.html         # shared nav partial
│   ├── home.html           # menu page
│   ├── cart.html           # cart & checkout
│   └── orders.html         # order history (IDOR target)
└── static/
    ├── css/style.css
    └── js/cart.js          # leaks X-User-ID via /api/cart/add
```
