from flask import Blueprint, request, redirect, session
from markupsafe import escape

from ui import render_page

bp = Blueprint("auth", __name__)

PUBLIC_PATHS = {"/", "/login", "/logout"}


def require_login_globally():
    path = request.path
    if path.startswith("/static"):
        return
    if path in PUBLIC_PATHS:
        return
    if not session.get("logged_in"):
        return redirect("/login")


@bp.route("/")
def home():
    return redirect("/login")


@bp.route("/login", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == "admin" and password == "admin":
            session["logged_in"] = True
            session["username"] = "admin"
            return redirect("/dashboard")
        else:
            error = "Invalid username or password"

    error_html = f"""
      <div class="card" style="border-color: rgba(255,92,122,.5); background: rgba(255,92,122,.08);">
        <div style="color: #ffb3c1; font-weight:700;">{escape(error)}</div>
      </div>
    """ if error else ""

    body = f"""
    <div style="display:grid; gap:14px;">
      <div class="card" style="max-width:520px;margin:40px auto;">
        <div style="text-align:center; padding:6px 0 10px;">
          <div style="font-size:54px; line-height:1;">🔧</div>
          <div style="font-size:22px; font-weight:800; margin-top:6px;">Workshop Manager</div>
          <div class="sub" style="margin-top:6px;">Login to continue</div>
        </div>

        {error_html}

        <form method="post" style="margin-top:10px;">
          <div class="field">
            <label>Username</label>
            <input name="username" placeholder="admin" required>
          </div>
          <div class="field">
            <label>Password</label>
            <input name="password" type="password" placeholder="admin" required>
          </div>
          <div class="actions" style="justify-content:center;">
            <button class="btn primary" type="submit">Login</button>
          </div>

          <div class="footer-note" style="text-align:center;">
          </div>
        </form>
      </div>

      <div class="card" style="max-width:520px;margin:0 auto;">
        <div style="font-weight:900; margin-bottom:6px;">Project Members</div>
        <ol style="margin:0; padding-left:18px; color: var(--text);">
          <li>Shahmir Ahmad</li>
          <li>Shahbaz Ali</li>
          <li>Ahsan Bilal</li>
        </ol>
      </div>
    </div>
    """
    return render_page("Login", "/login", body, "")


@bp.route("/dashboard")
def dashboard():
    username = session.get("username", "user")
    body = f"""
    <div class="card">
      <div class="actions" style="justify-content:space-between; align-items:center;">
        <div>
          <div style="font-weight:800; font-size:16px;">Welcome, {escape(username)} 👋</div>
          <div class="sub">Choose a module to continue</div>
        </div>
        <a class="btn" href="/logout">Logout</a>
      </div>
    </div>

    <div class="dash">
      <a class="dashcard" href="/customers"><div class="ico">👤</div><div class="ttl">Customers</div><div class="sub2">Manage customers</div></a>
      <a class="dashcard" href="/vehicles"><div class="ico">🚗</div><div class="ttl">Vehicles</div><div class="sub2">Customer vehicles</div></a>
      <a class="dashcard" href="/mechanics"><div class="ico">🧰</div><div class="ttl">Mechanics</div><div class="sub2">Staff & expertise</div></a>
      <a class="dashcard" href="/services"><div class="ico">🛠️</div><div class="ttl">Services</div><div class="sub2">Service catalog</div></a>
      <a class="dashcard" href="/parts"><div class="ico">⚙️</div><div class="ttl">Parts</div><div class="sub2">Inventory & stock</div></a>
      <a class="dashcard" href="/records"><div class="ico">🧾</div><div class="ttl">Service Records</div><div class="sub2">Jobs tracking</div></a>
      <a class="dashcard" href="/bills"><div class="ico">💳</div><div class="ttl">Bills</div><div class="sub2">Payments</div></a>
    </div>
    """
    return render_page("Dashboard", "/dashboard", body, "Workshop control panel")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

def init_app(app):
    app.before_request(require_login_globally)
