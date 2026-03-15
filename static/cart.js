// ─── Cart Storage ─────────────────────────────────────────────────────────────
function getCart() {
  try { return JSON.parse(sessionStorage.getItem('7aloshik_cart') || '[]'); }
  catch { return []; }
}

function saveCart(cart) {
  sessionStorage.setItem('7aloshik_cart', JSON.stringify(cart));
}

function updateCartBadge() {
  const total = getCart().reduce((a, i) => a + i.qty, 0);
  ['cartCount','navCartCount'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = total;
  });
}

// ─── Add to Cart ──────────────────────────────────────────────────────────────
async function addToCart(itemId, name, price) {
  // Call the API — this response will contain X-User-ID header (the vulnerability)
  const res = await fetch('/api/cart/add', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ item_id: itemId })
  });

  if (!res.ok) { console.error('Failed to add item'); return; }

  // Persist in sessionStorage
  const cart = getCart();
  const existing = cart.find(i => i.id === itemId);
  if (existing) {
    existing.qty += 1;
  } else {
    cart.push({ id: itemId, name, price, qty: 1 });
  }
  saveCart(cart);
  updateCartBadge();
  showToast(`${name} added to cart!`);
}

// ─── Toast Notification ───────────────────────────────────────────────────────
function showToast(msg) {
  const t = document.getElementById('cartToast');
  if (!t) return;
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2500);
}

// Init badge on page load
document.addEventListener('DOMContentLoaded', updateCartBadge);
