from flask import Blueprint, request, redirect
from markupsafe import escape

from db import get_conn
from ui import render_page, table

bp = Blueprint("customers", __name__)


@bp.route("/customers")
def customers():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT CustomerID, CustomerName, PhoneNumber, Address FROM Customer ORDER BY CustomerID ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    actions = """
    <div class="card">
      <div class="actions">
        <a class="btn primary" href="/add-customer">+ Add Customer</a>
      </div>
    </div>
    """

    def row_html(r):
        cid, name, phone, addr = r
        return (
            f"<tr>"
            f"<td>{cid}</td>"
            f"<td>{escape(name)}</td>"
            f"<td>{escape(phone)}</td>"
            f"<td>{escape(addr or '')}</td>"
            f"<td><a class='btn' href='/edit-customer/{cid}'>Edit</a></td>"
            f"</tr>"
        )

    t = table(["ID", "Name", "Phone", "Address", "Action"], rows, row_html)
    return render_page("Customers", "/customers", actions + t, "Manage customers and contact details")


@bp.route("/add-customer", methods=["GET", "POST"])
def add_customer():
    if request.method == "POST":
        name = request.form["name"].strip()
        phone = request.form["phone"].strip()
        address = request.form.get("address", "").strip()

        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Customer (CustomerName, PhoneNumber, Address) VALUES (%s, %s, %s)",
            (name, phone, address if address else None)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/customers")

    body = """
    <div class="card">
      <form method="post">
        <div class="field"><label>Customer Name</label><input name="name" required></div>
        <div class="field"><label>Phone Number</label><input name="phone" required></div>
        <div class="field"><label>Address</label><input name="address" placeholder="Optional"></div>
        <div class="actions">
          <button class="btn primary" type="submit">Save</button>
          <a class="btn" href="/customers">Cancel</a>
        </div>
      </form>
    </div>
    """
    return render_page("Add Customer", "/customers", body)


@bp.route("/edit-customer/<int:customer_id>", methods=["GET", "POST"])
def edit_customer(customer_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT CustomerName, PhoneNumber, Address FROM Customer WHERE CustomerID=%s", (customer_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return redirect("/customers")

    if request.method == "POST":
        name = request.form["name"].strip()
        phone = request.form["phone"].strip()
        address = request.form.get("address", "").strip()

        cur.execute(
            "UPDATE Customer SET CustomerName=%s, PhoneNumber=%s, Address=%s WHERE CustomerID=%s",
            (name, phone, address if address else None, customer_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/customers")

    name, phone, addr = row
    cur.close()
    conn.close()

    body = f"""
    <div class="card">
      <form method="post">
        <div class="field"><label>Customer Name</label><input name="name" value="{escape(name)}" required></div>
        <div class="field"><label>Phone Number</label><input name="phone" value="{escape(phone)}" required></div>
        <div class="field"><label>Address</label><input name="address" value="{escape(addr or '')}"></div>
        <div class="actions">
          <button class="btn primary" type="submit">Update</button>
          <a class="btn" href="/customers">Cancel</a>
        </div>
      </form>
    </div>
    """
    return render_page("Edit Customer", "/customers", body)
