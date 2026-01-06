from flask import Blueprint, request, redirect
from markupsafe import escape

from db import get_conn
from ui import render_page, table

bp = Blueprint("parts", __name__)


@bp.route("/parts")
def parts():
    LOW_STOCK = 5
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT PartID, PartName, Quantity, Price FROM Parts_Inventory ORDER BY PartID ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    actions = f"""
    <div class="card">
      <div class="actions">
        <a class="btn primary" href="/add-part">+ Add Part</a>
      </div>
      <div class="footer-note">Low stock threshold: {LOW_STOCK}. Use Restock/Use to update quantity.</div>
    </div>
    """

    def row_html(r):
        part_id, name, qty, price = r
        if qty <= 0:
            badge = "<span class='badge' style='border-color: rgba(255,92,122,.55)'>Out of stock</span>"
        elif qty <= LOW_STOCK:
            badge = "<span class='badge' style='border-color: rgba(255,92,122,.55)'>Low stock</span>"
        else:
            badge = "<span class='badge' style='border-color: rgba(45,212,191,.55)'>OK</span>"

        return (
            f"<tr>"
            f"<td>{part_id}</td>"
            f"<td>{escape(name)} {badge}</td>"
            f"<td>{qty}</td>"
            f"<td>{escape(str(price))}</td>"
            f"<td style='display:flex; gap:8px; align-items:center;'>"
            f"<a class='btn' href='/restock-part/{part_id}'>Restock</a>"
            f"<a class='btn danger' href='/use-part/{part_id}'>Use</a>"
            f"</td>"
            f"</tr>"
        )

    t = table(["Part ID", "Part Name", "Quantity", "Price", "Actions"], rows, row_html)
    return render_page("Parts Inventory", "/parts", actions + t, "Track parts stock and prices")


@bp.route("/add-part", methods=["GET", "POST"])
def add_part():
    if request.method == "POST":
        name = request.form["name"].strip()
        qty = int(request.form["qty"])
        price = request.form["price"]

        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Parts_Inventory (PartName, Quantity, Price) VALUES (%s, %s, %s)",
            (name, qty, price)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/parts")

    body = """
    <div class="card">
      <form method="post">
        <div class="field"><label>Part Name</label><input name="name" required></div>
        <div class="field"><label>Quantity</label><input name="qty" type="number" min="0" value="0" required></div>
        <div class="field"><label>Price</label><input name="price" type="number" step="0.01" min="0" required></div>
        <div class="actions">
          <button class="btn primary" type="submit">Save</button>
          <a class="btn" href="/parts">Cancel</a>
        </div>
      </form>
    </div>
    """
    return render_page("Add Part", "/parts", body)


@bp.route("/restock-part/<int:part_id>", methods=["GET", "POST"])
def restock_part(part_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT PartName, Quantity FROM Parts_Inventory WHERE PartID = %s", (part_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return redirect("/parts")

    name, qty_now = row

    if request.method == "POST":
        add_qty = int(request.form["qty"])
        cur.execute("UPDATE Parts_Inventory SET Quantity = Quantity + %s WHERE PartID = %s", (add_qty, part_id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/parts")

    cur.close()
    conn.close()

    body = f"""
    <div class="card">
      <form method="post">
        <div class="field"><label>Part</label><input value="{escape(name)}" disabled></div>
        <div class="field"><label>Current Quantity</label><input value="{qty_now}" disabled></div>
        <div class="field"><label>Add Quantity</label><input name="qty" type="number" min="1" value="1" required></div>
        <div class="actions">
          <button class="btn primary" type="submit">Update</button>
          <a class="btn" href="/parts">Cancel</a>
        </div>
      </form>
    </div>
    """
    return render_page("Restock Part", "/parts", body)


@bp.route("/use-part/<int:part_id>", methods=["GET", "POST"])
def use_part(part_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT PartName, Quantity FROM Parts_Inventory WHERE PartID = %s", (part_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return redirect("/parts")

    name, qty_now = row

    if request.method == "POST":
        use_qty = int(request.form["qty"])
        cur.execute("""
            UPDATE Parts_Inventory
            SET Quantity = GREATEST(Quantity - %s, 0)
            WHERE PartID = %s
        """, (use_qty, part_id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/parts")

    cur.close()
    conn.close()

    body = f"""
    <div class="card">
      <form method="post">
        <div class="field"><label>Part</label><input value="{escape(name)}" disabled></div>
        <div class="field"><label>Current Quantity</label><input value="{qty_now}" disabled></div>
        <div class="field"><label>Quantity Used</label><input name="qty" type="number" min="1" value="1" required></div>
        <div class="actions">
          <button class="btn danger" type="submit">Use</button>
          <a class="btn" href="/parts">Cancel</a>
        </div>
      </form>
      <div class="footer-note">Stock will never go below 0.</div>
    </div>
    """
    return render_page("Use Part", "/parts", body)
